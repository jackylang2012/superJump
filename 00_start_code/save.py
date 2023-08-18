import pickle
import json

class SaveGame:

    def __init__(self, name, archive, image, item_id):
        self.name = name
        self.id = item_id
        self.archive = archive
        self.image = image

    def display_info(self):
        print(f"Item ID: {self.id}")
        print(f"Name: {self.name}")
        print(f"Archives: {self.archive}")
        print(f"Image: {self.image}")

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "archive": self.archive,
            "image": self.image
        }

def save_items_to_json(items, filename):
    items_data = [item.to_dict() for item in items]
    with open(filename, 'w') as file:
        json.dump(items_data, file, indent=4)

def load_items_from_json(filename):
    with open(filename, 'r') as file:
        items_data = json.load(file)
        items = []
        for item_data in items_data:
            item = SaveGame(item_data["name"], item_data["archive"], item_data["image"], item_data["id"])
            items.append(item)
        return items

# 创建一些 SaveGame 实例
items_to_save = [
    SaveGame("Item 1", "Archive 1", "image1.jpg", 1),
    SaveGame("Item 2", "Archive 2", "image2.jpg", 2)
]

# 将实例列表保存为 JSON 文件
save_items_to_json(items_to_save, "saved_items.json")

# 从 JSON 文件加载实例列表
loaded_items = load_items_from_json("saved_items.json")

# 显示加载的实例信息
for item in loaded_items:
    item.display_info()
