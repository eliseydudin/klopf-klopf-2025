import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    TimeDistributed,
    LSTM,
    Dense,
    Dropout,
    GlobalAveragePooling2D,
)
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import Sequence
from sklearn.model_selection import train_test_split
import argparse

# ===================== КОНФИГУРАЦИЯ ДЛЯ APPLE M4  =====================
DATASET_DIR = "dataset"  # Папка с данными (структура: dataset/falls/, dataset/fights/)
NUM_CLASSES = 2  # 2 класса: падения и драки
SEQ_LENGTH = 24
IMAGE_SIZE = (256, 256)
BATCH_SIZE = 4
EPOCHS = 30
MODEL_PATH = "custom_model2.h5"  # Путь для сохранения модели


# ===================== ПРОВЕРКА И НАСТРОЙКА ДЛЯ APPLE M4  =====================
def setup_environment():
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        try:
            tf.config.set_logical_device_configuration(
                gpus[0], [tf.config.LogicalDeviceConfiguration(memory_limit=20336)]
            )
            # Включаем mixed precision для ускорения вычислений
            policy = tf.keras.mixed_precision.Policy("mixed_float16")
            tf.keras.mixed_precision.set_global_policy(policy)
            print(
                "✅ Используем GPU с Metal Performance Shaders (MPS) и mixed precision"
            )
        except RuntimeError as e:
            print(f"⚠️ Ошибка настройки GPU: {e}")
            print("Используем только CPU")
    else:
        print("Используем только CPU")


# ===================== ИЗВЛЕЧЕНИЕ КАДРОВ ИЗ ВИДЕО =====================
def extract_frames_from_video(video_path, output_dir, class_name, frame_rate=5):
    """Извлекает кадры из видео файла любого формата и сохраняет в папку с кадрами"""
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    frames_dir = os.path.join(output_dir, class_name, f"{video_name}_frames")
    os.makedirs(frames_dir, exist_ok=True)

    if os.listdir(frames_dir):
        return frames_dir

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Не удалось открыть видео: {video_path}")
        if os.path.exists(frames_dir) and not os.listdir(frames_dir):
            os.rmdir(frames_dir)
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps > 30:
        frame_rate = 2
    elif fps > 20:
        frame_rate = 3
    else:
        frame_rate = 5

    saved_count = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_rate == 0:
            frame_path = os.path.join(frames_dir, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            saved_count += 1

        frame_count += 1

    cap.release()

    if saved_count == 0:
        os.rmdir(frames_dir)
        print(f"❌ Не извлечено ни одного кадра из {video_path}")
        return None

    print(f"✅ Извлечено {saved_count} кадров из {video_name} (FPS: {fps:.1f})")
    return frames_dir


# ===================== ГЕНЕРАТОР ДАННЫХ С АУГМЕНТАЦИЕЙ =====================
class VideoSequenceGenerator(Sequence):
    def __init__(
        self,
        video_dirs,
        labels,
        batch_size=32,
        seq_length=16,
        image_size=(224, 224),
        is_training=True,
    ):
        self.video_dirs = video_dirs
        self.labels = labels
        self.batch_size = batch_size
        self.seq_length = seq_length
        self.image_size = image_size
        self.is_training = is_training
        self.indices = np.arange(len(video_dirs))
        np.random.shuffle(self.indices)

    def __len__(self):
        return len(self.video_dirs) // self.batch_size

    def __getitem__(self, index):
        batch_indices = self.indices[
            index * self.batch_size : (index + 1) * self.batch_size
        ]
        batch_videos = [self.video_dirs[i] for i in batch_indices]
        batch_labels = [self.labels[i] for i in batch_indices]

        X = []
        y = []

        for video_dir in batch_videos:
            frames = self.load_frames(video_dir)
            # Выбираем seq_length кадров
            if len(frames) < self.seq_length:
                while len(frames) < self.seq_length:
                    frames.append(frames[-1])
            else:
                step = len(frames) // self.seq_length
                frames = [frames[i * step] for i in range(self.seq_length)]

            if self.is_training:
                processed_frames = [self.apply_augmentation(frame) for frame in frames]
            else:
                processed_frames = [self.preprocess_frame(frame) for frame in frames]

            X.append(processed_frames)
            y.append(batch_labels[0])

        return np.array(X), np.array(y)

    def load_frames(self, video_dir):
        """Загружает кадры из папки видео"""
        frames = []
        frame_files = sorted(
            [f for f in os.listdir(video_dir) if f.endswith((".jpg", ".jpeg", ".png"))]
        )

        for frame_file in frame_files:
            frame_path = os.path.join(video_dir, frame_file)
            frame = cv2.imread(frame_path)
            if frame is not None:
                frames.append(frame)
        return frames

    def apply_augmentation(self, frame):
        """Применяет аугментацию к кадру"""
        if np.random.random() > 0.3:
            alpha = 0.8 + np.random.random() * 0.4
            beta = np.random.randint(-30, 30)
            frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

        if np.random.random() > 0.5:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv = hsv.astype(np.float32)
            hsv[:, :, 0] = (hsv[:, :, 0] + np.random.randint(-10, 10)) % 180
            hsv[:, :, 1] = np.clip(
                hsv[:, :, 1] * (0.8 + np.random.random() * 0.4), 0, 255
            )
            frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        if np.random.random() > 0.5:
            if np.random.random() > 0.5:
                frame = cv2.flip(frame, 1)
            else:
                angle = np.random.randint(-15, 15)
                h, w = frame.shape[:2]
                M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
                frame = cv2.warpAffine(frame, M, (w, h))

        return self.preprocess_frame(frame)

    def preprocess_frame(self, frame):
        frame = cv2.resize(frame, self.image_size)
        frame = preprocess_input(frame)
        return frame

    def on_epoch_end(self):
        np.random.shuffle(self.indices)


# ===================== СОЗДАНИЕ МОДЕЛИ =====================
def build_model():
    """Создает модель TimeDistributed ResNet50 + LSTM"""
    base_model = ResNet50(
        weights="imagenet",
        include_top=False,
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3),
    )
    base_model.trainable = False

    frame_model = Model(inputs=base_model.input, outputs=base_model.output)

    model = Sequential()
    model.add(
        TimeDistributed(
            frame_model, input_shape=(SEQ_LENGTH, IMAGE_SIZE[0], IMAGE_SIZE[1], 3)
        )
    )
    model.add(TimeDistributed(GlobalAveragePooling2D()))
    model.add(LSTM(128, return_sequences=False))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(NUM_CLASSES, activation="softmax"))

    model.compile(
        optimizer=Adam(learning_rate=1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.summary()
    return model


# ===================== ПОДГОТОВКА ДАННЫХ =====================
def prepare_data():
    """Автоматически готовит данные из видео файлов в папке dataset"""
    video_dirs = []
    labels = []
    class_names = sorted(
        [
            d
            for d in os.listdir(DATASET_DIR)
            if os.path.isdir(os.path.join(DATASET_DIR, d))
        ]
    )

    print(f"Найдено классов: {len(class_names)} - {class_names}")

    for class_idx, class_name in enumerate(class_names):
        class_dir = os.path.join(DATASET_DIR, class_name)
        for file in os.listdir(class_dir):
            if file.endswith(
                (".mp4", ".mpeg", ".mpg", ".mov", ".avi", ".mkv", ".wmv", ".flv")
            ):
                video_path = os.path.join(class_dir, file)
                print(f"Обработка видео: {file} (класс: {class_name})")
                frames_dir = extract_frames_from_video(
                    video_path, DATASET_DIR, class_name
                )
                if frames_dir is None:
                    continue
                video_dirs.append(frames_dir)
                labels.append(class_idx)

    print(f"✅ Всего обработано видео: {len(video_dirs)}")
    return train_test_split(video_dirs, labels, test_size=0.2, random_state=42)


# ===================== ОБУЧЕНИЕ МОДЕЛИ =====================
def train_model(model_path=MODEL_PATH):
    train_videos, val_videos, train_labels, val_labels = prepare_data()

    train_generator = VideoSequenceGenerator(
        train_videos,
        train_labels,
        batch_size=BATCH_SIZE,
        seq_length=SEQ_LENGTH,
        image_size=IMAGE_SIZE,
        is_training=True,
    )

    val_generator = VideoSequenceGenerator(
        val_videos,
        val_labels,
        batch_size=BATCH_SIZE,
        seq_length=SEQ_LENGTH,
        image_size=IMAGE_SIZE,
        is_training=False,
    )

    model = build_model()

    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=3, restore_best_weights=True, verbose=1
    )

    model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
        model_path, monitor="val_accuracy", save_best_only=True, verbose=1
    )

    history = model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=EPOCHS,
        steps_per_epoch=len(train_generator),
        validation_steps=len(val_generator),
        callbacks=[early_stop, model_checkpoint],
        verbose=1,
    )

    print(f"✅ Модель сохранена в {model_path}")
    return model


# ===================== ПРОГНОЗИРОВАНИЕ НА НОВОМ ВИДЕО =====================
def predict_incident(video_path, model_path=MODEL_PATH):
    model = tf.keras.models.load_model(model_path)

    frames_dir = extract_frames_from_video(
        video_path, DATASET_DIR, "temp", frame_rate=3
    )
    if frames_dir is None:
        print(f"❌ Не удалось обработать видео: {video_path}")
        return None, None

    generator = VideoSequenceGenerator(
        [frames_dir],
        [0],
        batch_size=1,
        seq_length=SEQ_LENGTH,
        image_size=IMAGE_SIZE,
        is_training=False,
    )

    X, _ = generator[0]
    prediction = model.predict(X)[0]
    class_idx = np.argmax(prediction)

    class_names = sorted(
        [
            d
            for d in os.listdir(DATASET_DIR)
            if os.path.isdir(os.path.join(DATASET_DIR, d))
        ]
    )
    class_name = class_names[class_idx]

    print(f"\n{'=' * 50}")
    # print(f"Результат для: {os.path.basename(video_path)}")
    print(f"Тип инцидента: {class_name}")
    print(f"Вероятность: {prediction[class_idx]:.2%}")
    print(
        f"Другие классы: {[f'{c}: {p:.2%}' for c, p in zip(class_names, prediction)]}"
    )
    print(f"{'=' * 50}\n")
    return class_name, prediction


# ===================== ЗАПУСК С КОМАНДНОЙ СТРОКОЙ =====================
def main():
    parser = argparse.ArgumentParser(
        description="Система распознавания инцидентов для Apple M4 Pro"
    )
    parser.add_argument(
        "--mode",
        choices=["train", "predict"],
        required=True,
        help="Режим работы: train - обучение модели, predict - анализ видео",
    )
    parser.add_argument(
        "--video",
        type=str,
        default="test_video.mp4",
        help="Путь к видео для анализа (только для режима predict)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=MODEL_PATH,
        help="Путь для сохранения/загрузки модели",
    )

    args = parser.parse_args()

    setup_environment()

    if args.mode == "train":
        print("\n" + "=" * 50)
        print("ЗАПУСК РЕЖИМА ОБУЧЕНИЯ")
        print("=" * 50 + "\n")
        train_model(args.model)
        print("\n" + "=" * 50)
        print("ОБУЧЕНИЕ ЗАВЕРШЕНО")
        print("=" * 50)

    elif args.mode == "predict":
        print("\n" + "=" * 50)
        print("ЗАПУСК РЕЖИМА АНАЛИЗА")
        print("=" * 50 + "\n")

        if not os.path.exists(args.model):
            print(
                f"❌ Ошибка: Файл модели {args.model} не найден. Сначала обучите модель."
            )
            return

        if not os.path.exists(args.video):
            print(f"❌ Ошибка: Файл видео {args.video} не найден.")
            return

        predict_incident(args.video, args.model)
        print("\n" + "=" * 50)
        print("АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 50)


if __name__ == "__main__":
    main()
