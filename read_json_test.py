import json

# JSONファイルを読み込む
def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# "movement" のリストを取得する関数
def get_movement_list(data):
    return [item["movement"] for item in data]

# "movement" で検索する関数
def search_by_movement(data, movement_name):
    result = [item for item in data if item["movement"] == movement_name]
    return result

# メイン処理
if __name__ == "__main__":
    import sys
    data = load_json_file(sys.argv[1])
    
    # 利用可能な "movement" のリストを表示
    movement_list = get_movement_list(data)
    print("Available movements:")
    for i, movement in enumerate(movement_list, 1):
        print(f"{i}: {movement}")
    
    # ユーザーに選択を促す
    try:
        choice = int(input("Select the movement by number: ")) - 1
        if 0 <= choice < len(movement_list):
            selected_movement = movement_list[choice]
            # 検索結果を取得
            search_result = search_by_movement(data, selected_movement)
            
            # 検索結果を表示
            if search_result:
                print("Found the following entries:")
                for entry in search_result:
                    print(json.dumps(entry, indent=4))
            else:
                print(f"No entries found for movement: {selected_movement}")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input. Please enter a number.")
