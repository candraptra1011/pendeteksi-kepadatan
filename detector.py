from ultralytics import YOLO
from density import get_density
from trafficlight import get_traffic_light

import cv2
import os

# ==========================================
# LOAD MODEL
# ==========================================

model = YOLO("yolov5su.pt")

# ==========================================
# ROI (AREA PENGAMATAN)
# ==========================================

ROI_X1 = 650
ROI_Y1 = 260

ROI_X2 = 1090
ROI_Y2 = 760

# ==========================================
# PROSES VIDEO
# ==========================================

def process_video(video_path):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():

        return {
            "video": "",
            "average": 0,
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0,
            "density": "Error",
            "green": 0,
            "red": 0
        }

    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Mencegah pembagian dengan nol jika FPS video tidak terbaca
    if fps <= 0:
        fps = 30

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    os.makedirs("static/output", exist_ok=True)

    output_path = "static/output/hasil.mp4"

    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height)
    )

    # ==========================================
    # PENYIMPAN DATA
    # ==========================================

    total_per_second = []

    car_per_second = []

    motorcycle_per_second = []

    bus_per_second = []

    truck_per_second = []

    frame_total = []

    frame_car = []

    frame_motorcycle = []

    frame_bus = []

    frame_truck = []

    frame_count = 0

    # ==========================================
    # MULAI MEMBACA VIDEO
    # ==========================================

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[2, 3, 5, 7],
            conf=0.35,
            verbose=False
        )

        result = results[0]

        car = 0
        motorcycle = 0
        bus = 0
        truck = 0

        if result.boxes.cls is not None:

            boxes = result.boxes.xyxy.cpu().numpy()

            classes = result.boxes.cls.cpu().numpy().astype(int)

            ids = None

            if result.boxes.id is not None:
                ids = result.boxes.id.cpu().numpy().astype(int)

            for i, (box, cls) in enumerate(zip(boxes, classes)):

                x1, y1, x2, y2 = map(int, box)

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # ==========================================
                # CEK APAKAH BOUNDING BOX BERIRISAN DENGAN ROI
                # ==========================================

                if (
                    x2 < ROI_X1 or
                    x1 > ROI_X2 or
                    y2 < ROI_Y1 or
                    y1 > ROI_Y2
                ):
                    continue

                label = model.names[cls]

                if label == "car":
                    car += 1

                elif label == "motorcycle":
                    motorcycle += 1

                elif label == "bus":
                    bus += 1

                elif label == "truck":
                    truck += 1

                # ==========================================
                # GAMBAR BOUNDING BOX
                # ==========================================

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                if ids is not None:
                    text = f"{label} ID:{ids[i]}"
                else:
                    text = label

                cv2.putText(
                    frame,
                    text,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

                # ==========================================
                # TITIK TENGAH
                # ==========================================

                cv2.circle(
                    frame,
                    (cx, cy),
                    4,
                    (0, 0, 255),
                    -1
                )

        # ==========================================
        # GAMBAR ROI
        # ==========================================

        cv2.rectangle(
            frame,
            (ROI_X1, ROI_Y1),
            (ROI_X2, ROI_Y2),
            (255, 0, 0),
            3
        )

        cv2.putText(
            frame,
            "ROI",
            (ROI_X1, ROI_Y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

        # ==========================================
        # TOTAL FRAME SAAT INI
        # ==========================================

        total = (
            car +
            motorcycle +
            bus +
            truck
        )

        # ==========================================
        # SIMPAN HASIL SETIAP FRAME
        # ==========================================

        frame_total.append(total)

        frame_car.append(car)

        frame_motorcycle.append(motorcycle)

        frame_bus.append(bus)

        frame_truck.append(truck)

        # ==========================================
        # SETIAP 1 DETIK AMBIL NILAI TERTINGGI
        # ==========================================

        if frame_count % fps == 0:

            total_per_second.append(
                max(frame_total)
            )

            print("==============================")
            print("FRAME TOTAL :", frame_total)
            print("NILAI TERTINGGI :", max(frame_total))
            print("==============================")

            car_per_second.append(
                max(frame_car)
            )

            motorcycle_per_second.append(
                max(frame_motorcycle)
            )

            bus_per_second.append(
                max(frame_bus)
            )

            truck_per_second.append(
                max(frame_truck)
            )

            frame_total.clear()

            frame_car.clear()

            frame_motorcycle.clear()

            frame_bus.clear()

            frame_truck.clear()

        # ==========================================
        # TAMPILKAN INFORMASI PADA VIDEO OUTPUT
        # ==========================================

        cv2.putText(
            frame,
            f"Peak Vehicle : {max(frame_total) if len(frame_total) > 0 else total}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Car : {car}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Motorcycle : {motorcycle}",
            (20, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Bus : {bus}",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Truck : {truck}",
            (20, 185),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Second : {frame_count // fps}",
            (20, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # ==========================================
        # SIMPAN FRAME KE VIDEO OUTPUT
        # ==========================================

        writer.write(frame)

    # ==========================================
    # SELESAI MEMBACA VIDEO
    # ==========================================

    cap.release()

    writer.release()

    # Tidak menggunakan cv2.destroyAllWindows()
    # karena aplikasi berjalan di server tanpa GUI.

    # ==========================================
    # SISA FRAME YANG BELUM 1 DETIK
    # ==========================================

    if len(frame_total) > 0:

        total_per_second.append(
            max(frame_total)
        )

        car_per_second.append(
            max(frame_car)
        )

        motorcycle_per_second.append(
            max(frame_motorcycle)
        )

        bus_per_second.append(
            max(frame_bus)
        )

        truck_per_second.append(
            max(frame_truck)
        )

    # ==========================================
    # CEK HASIL DETEKSI
    # ==========================================

    if len(total_per_second) == 0:

        return {
            "video": "/" + output_path.replace("\\", "/"),
            "average": 0,
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0,
            "density": "Error",
            "green": 0,
            "red": 0
        }

    # ==========================================
    # HITUNG RATA-RATA DARI NILAI TERTINGGI TIAP DETIK
    # ==========================================

    average_vehicle = round(
        sum(total_per_second) /
        len(total_per_second)
    )

    average_car = round(
        sum(car_per_second) /
        len(car_per_second)
    )

    average_motorcycle = round(
        sum(motorcycle_per_second) /
        len(motorcycle_per_second)
    )

    average_bus = round(
        sum(bus_per_second) /
        len(bus_per_second)
    )

    average_truck = round(
        sum(truck_per_second) /
        len(truck_per_second)
    )

    # ==========================================
    # TENTUKAN KEPADATAN
    # ==========================================

    density = get_density(
        average_vehicle
    )

    # ==========================================
    # REKOMENDASI LAMPU LALU LINTAS
    # ==========================================

    traffic = get_traffic_light(
        density
    )

    # ==========================================
    # HASIL
    # ==========================================

    return {

        "video": "/" + output_path.replace("\\", "/"),

        "average": average_vehicle,

        "car": average_car,

        "motorcycle": average_motorcycle,

        "bus": average_bus,

        "truck": average_truck,

        "density": density,

        "green": traffic["green"],

        "red": traffic["red"]

    }
