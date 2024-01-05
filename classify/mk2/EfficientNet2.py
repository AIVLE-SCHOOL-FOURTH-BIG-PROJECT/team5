import pandas as pd
import numpy as np
from PIL import Image
import ast
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers
import tensorflow_addons as tfa
import math
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

# GPU 메모리 설정
# Set the GPU memory growth option
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # Restrict TensorFlow to allocate only the first GPU
        tf.config.set_visible_devices(gpus[0], 'GPU')
        # Enable memory growth to allocate GPU memory on an as-needed basis
        tf.config.experimental.set_memory_growth(gpus[0], True)
        # Set the = activationdesired memory limit (in MB)
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0],
            [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=10240)]
        )
    except RuntimeError as e:
        print(e)
        
        
home_office_desks_df = pd.read_pickle("/home/myeong/home_office_desks_df.pkl")

# 유니크 추출(styles변수)
import ast

def extract_all_styles(df, info_column='Product_Info'):
    """
    데이터프레임에서 가능한 모든 스타일을 추출합니다.

    :param df: pandas DataFrame, 'Product_Info' 열이 포함된 데이터프레임
    :param info_column: 스타일 정보가 포함된 열의 이름
    :return: 집합 형태로 모든 유니크 스타일
    """
    styles = set()
    for info in df[info_column]:
        try:
            product_info = ast.literal_eval(info)
            style = product_info.get('Style', '').lower()
            if style:
                styles.add(style)
        except ValueError:
            continue  # 파싱 에러가 발생한 경우 건너뜀
    return styles

# 모든 유니크 스타일 추출
styles = extract_all_styles(home_office_desks_df)
styles = list(styles)

# 데이터 준비
def extract_style(info):
    info_dict = eval(info)
    return styles.index(info_dict['Style'].lower()) if 'Style' in info_dict and info_dict['Style'].lower() in styles else -1

# 레이블과 이미지 경로 추출
labels = []
image_paths = []
for _, row in home_office_desks_df.iterrows():
    style_index = extract_style(row['Product_Info'])
    if style_index != -1:
        labels.append(style_index)
        image_paths.append(row['img_path'])

# 레이블을 원-핫 인코딩으로 변환
labels = tf.keras.utils.to_categorical(labels, num_classes=len(styles))

default_resolution = 256
# 이미지 로드 및 전처리
def process_image(image_path):
    img = load_img(image_path, target_size=(default_resolution, default_resolution))
    img_array = img_to_array(img)
    img_array = img_array / 255.0  # 정규화
    return img_array

# 이미지 로드
images = np.array([process_image(path) for path in image_paths])

# 데이터 분할
X_train, X_temp, y_train, y_temp = train_test_split(images, labels, test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)


# EfficientNet 모델 구성
input_channels = 3
se_ratio = 4
expand_ratio = 6
width_coefficient = 1.0
depth_coefficient = 1.0
default_resolution = 256
depth_divisor= 8 
dropout_rate = 0.2
drop_connect_rate = 0.2

kernel_size = [3,3,5,3,5,5,3]
num_repeat = [1,2,2,3,3,4,1]
output_filters = [16,24,40,80,112,192,320]
strides = [1,2,2,2,1,2,1]
MBConvBlock_1_True  =  [True,False,False,False,False,False,False]

def round_repeats(repeats, depth_coefficient):
    return int(math.ceil(depth_coefficient * repeats))

def round_filters(filters, width_coefficient, depth_divisor):
    filters *= width_coefficient
    new_filters = int(filters + depth_divisor / 2) // depth_divisor * depth_divisor
    new_filters = max(depth_divisor, new_filters)
    if new_filters < 0.9 * filters:
        new_filters += depth_divisor
    return int(new_filters)

K = tf.keras.backend
class DropConnect(layers.Layer):
    def __init__(self, drop_connect_rate=0.0, **kwargs):
        super().__init__(**kwargs)
        self.drop_connect_rate = drop_connect_rate

    def call(self, inputs, training=None):
        if training:
            keep_prob = 1.0 - self.drop_connect_rate
            batch_size = tf.shape(inputs)[0]
            random_tensor = keep_prob
            random_tensor += K.random_uniform([batch_size, 1, 1, 1], dtype=inputs.dtype)
            binary_tensor = tf.floor(random_tensor)
            output = tf.math.divide(inputs, keep_prob) * binary_tensor
            return output
        else:
            return inputs

def SEBlock(filters,reduced_filters):
    def _block(inputs):
        x = layers.GlobalAveragePooling2D()(inputs)
        x = layers.Reshape((1,1,x.shape[1]))(x)
        x = layers.Conv2D(reduced_filters, 1, 1)(x)
        x = tfa.activations.mish(x)
        x = layers.Conv2D(filters, 1, 1)(x)
        x = layers.Activation('sigmoid')(x)
        x = layers.Multiply()([x, inputs])
        return x
    return _block

def MBConvBlock(x,kernel_size, strides,drop_connect_rate,output_channels,MBConvBlock_1_True=False):
    output_channels = round_filters(output_channels,width_coefficient,depth_divisor)
    if MBConvBlock_1_True:
        block = layers.DepthwiseConv2D(kernel_size, strides,padding='same', use_bias=False)(x)
        block = layers.BatchNormalization()(block)
        block = tfa.activations.mish(block)
        block = SEBlock(x.shape[3],x.shape[3]/se_ratio)(block)
        block = layers.Conv2D(output_channels, (1,1), padding='same', use_bias=False)(block)
        block = layers.BatchNormalization()(block)
        return block

    channels = x.shape[3]
    expand_channels = channels * expand_ratio
    block = layers.Conv2D(expand_channels, (1,1), padding='same', use_bias=False)(x)
    block = layers.BatchNormalization()(block)
    block = tfa.activations.mish(block)
    block = layers.DepthwiseConv2D(kernel_size, strides,padding='same', use_bias=False)(block)
    block = layers.BatchNormalization()(block)
    block = tfa.activations.mish(block)
    block = SEBlock(expand_channels,channels/se_ratio)(block)
    block = layers.Conv2D(output_channels, (1,1), padding='same', use_bias=False)(block)
    block = layers.BatchNormalization()(block)
    if x.shape[3] == output_channels:
        block = DropConnect(drop_connect_rate)(block)
        block = layers.Add()([block, x])
    return block

def EffNet(num_classes):
    x_input = layers.Input(shape=(default_resolution,default_resolution,input_channels))    
    x = layers.Conv2D(round_filters(32, width_coefficient, depth_divisor), (3,3), 2,padding='same', use_bias=False)(x_input)
    x = layers.BatchNormalization()(x)
    x = tfa.activations.mish(x)
    num_blocks_total = sum(num_repeat)
    block_num = 0
    for i in range(len(kernel_size)):
        round_num_repeat = round_repeats(num_repeat[i], depth_coefficient)
        drop_rate = drop_connect_rate * float(block_num) / num_blocks_total
        x = MBConvBlock(x,kernel_size[i],strides[i],drop_rate,output_filters[i],MBConvBlock_1_True = MBConvBlock_1_True[i])
        block_num += 1
        if round_num_repeat > 1:
            for bidx in range(round_num_repeat - 1):
                drop_rate = drop_connect_rate * float(block_num) / num_blocks_total
                x = MBConvBlock(x,kernel_size[i],1,drop_rate,output_filters[i],MBConvBlock_1_True = MBConvBlock_1_True[i])
                block_num += 1
    x = layers.Conv2D(round_filters(1280, width_coefficient, depth_divisor), 1,padding='same',use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = tfa.activations.mish(x)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(dropout_rate)(x)
    x = layers.Dense(len(styles), activation='softmax')(x)
    model = tf.keras.models.Model(inputs=x_input, outputs=x)
    return model


# 모델 정의 및 컴파일
model = EffNet(num_classes=len(styles))
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

early_stopper = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# 모델 학습
history = model.fit(X_train, y_train, batch_size=8, epochs=10, validation_data=(X_val, y_val), callbacks=[early_stopper], verbose=1)

# 테스트 세트에서 모델 평가
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {test_acc}")


# 모델을 사용하여 테스트 세트에 대한 예측을 수행
predictions = model.predict(X_test)
predicted_classes = np.argmax(predictions, axis=1)
true_classes = np.argmax(y_test, axis=1)

# 혼동 행렬 생성
cm = confusion_matrix(true_classes, predicted_classes)

# 혼동 행렬 시각화
plt.figure(figsize=(10, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=styles, yticklabels=styles)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

# 학습 및 검증 정확도 그래프
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

# 학습 및 검증 손실 그래프
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()

# 모델 저장
model_save_path = '/home/myeong/Desks_model.h5'  # .h5 확장자를 사용
model.save(model_save_path)
print(f"Model saved to {model_save_path}")






















