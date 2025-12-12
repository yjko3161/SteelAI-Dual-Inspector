import os
import glob
import shutil
import xml.etree.ElementTree as ET
from tqdm import tqdm

# === ⚙️ 설정 (경로를 본인 환경에 맞게 수정하세요) ===
# 압축 푼 원본 데이터 경로 (스크린샷의 'NEU-DET' 폴더 경로)
SOURCE_ROOT = './NEU-DET' 

# 변환된 데이터가 저장될 경로 (이 폴더가 새로 생성됩니다)
OUTPUT_DIR = './neu_yolo_data'

# 클래스 정의 (폴더명과 정확히 일치해야 함)
CLASSES = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']

def convert_box(size, box):
    """ XML 좌표(xmin, xmax...)를 YOLO 좌표(x_center, y_center, w, h)로 변환 """
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    return (x * dw, y * dh, w * dw, h * dh)

def convert_annotation(xml_file):
    """ XML 파일을 읽어 YOLO 포맷 문자열 리스트로 반환 """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)
        
        yolo_lines = []
        for obj in root.iter('object'):
            cls = obj.find('name').text
            if cls not in CLASSES:
                continue
            cls_id = CLASSES.index(cls)
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
                 float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
            bb = convert_box((w, h), b)
            yolo_lines.append(f"{cls_id} {bb[0]:.6f} {bb[1]:.6f} {bb[2]:.6f} {bb[3]:.6f}")
        return yolo_lines
    except Exception as e:
        # XML이 깨져있거나 없는 경우
        return []

def main():
    # 1. 저장할 폴더 구조 생성
    for split in ['train', 'val']:
        os.makedirs(os.path.join(OUTPUT_DIR, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_DIR, 'labels', split), exist_ok=True)

    # 2. 원본 폴더(validation) -> 타겟 폴더(val) 매핑
    # 스크린샷에 'validation'이라고 되어 있으므로 이를 'val'로 변경해줍니다.
    split_map = {'train': 'train', 'validation': 'val'}

    for source_split, target_split in split_map.items():
        print(f"🚀 Processing {source_split} data...")
        
        # 이미지/라벨 원본 경로
        src_img_root = os.path.join(SOURCE_ROOT, source_split, 'images')
        src_xml_root = os.path.join(SOURCE_ROOT, source_split, 'annotations')

        # 각 클래스 폴더(crazing, inclusion 등) 순회
        for cls_name in CLASSES:
            class_img_dir = os.path.join(src_img_root, cls_name)
            
            if not os.path.exists(class_img_dir):
                continue

            # 이미지 파일 찾기 (jpg, bmp, png)
            images = []
            for ext in ['*.jpg', '*.bmp', '*.png']:
                images.extend(glob.glob(os.path.join(class_img_dir, ext)))

            for img_path in tqdm(images, desc=f"{source_split}/{cls_name}"):
                filename = os.path.basename(img_path)
                file_id = os.path.splitext(filename)[0]

                # 3. XML 파일 찾기 로직
                # 경우의 수 A: annotations 폴더 바로 안에 xml이 있는 경우
                xml_path = os.path.join(src_xml_root, file_id + '.xml')
                
                # 경우의 수 B: annotations/클래스명 폴더 안에 xml이 있는 경우 (혹시 모를 대비)
                if not os.path.exists(xml_path):
                    xml_path = os.path.join(src_xml_root, cls_name, file_id + '.xml')
                
                if not os.path.exists(xml_path):
                    # 라벨 파일이 없으면 이미지도 스킵합니다.
                    continue

                # 4. 변환 및 복사
                yolo_data = convert_annotation(xml_path)
                if not yolo_data:
                    continue

                # 이미지 복사 (Flattening: 클래스 폴더 없이 다 모음)
                target_img_path = os.path.join(OUTPUT_DIR, 'images', target_split, filename)
                shutil.copy(img_path, target_img_path)

                # 라벨 저장
                target_lbl_path = os.path.join(OUTPUT_DIR, 'labels', target_split, file_id + '.txt')
                with open(target_lbl_path, 'w') as f:
                    f.write('\n'.join(yolo_data))

    print(f"\n✅ 변환 완료! 생성된 데이터 위치: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == '__main__':
    main()