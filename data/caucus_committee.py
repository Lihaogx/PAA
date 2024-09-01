import json
import pandas as pd
import os


def clean_text(text):
    # 确保值为字符串并清理文本
    return str(text).strip().strip('"').strip()


def load_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_personal_profiles(folder_path):
    profiles = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith('_profile.json'):
            file_path = os.path.join(folder_path, file_name)
            profile_data = load_json_file(file_path)
            person_name = file_name.replace('_profile.json', '')
            profiles[person_name] = profile_data
    return profiles


def process_csv(csv_filename, caucus_json_filename, committee_json_filename):
    # 读取CSV文件
    df = pd.read_csv(csv_filename)

    # 加载JSON数据
    caucus_data = load_json_file(caucus_json_filename)
    committee_data = load_json_file(committee_json_filename)

    # 匹配caucus数据
    caucus_matches = []
    for _, row in df.iterrows():
        bill_number = row['Bill Number']
        bill_name = row['Bill Name']
        caucus_name = clean_text(row['Caucus'])

        # 寻找匹配的caucus
        matched_caucus = next((item for item in caucus_data if item['Caucus'] == caucus_name), None)

        if matched_caucus:
            caucus_matches.append({
                "Bill Number": bill_number,
                "Bill Name": bill_name,
                "Caucus": matched_caucus
            })
        else:
            print(f"Caucus not found: {caucus_name}")

    # 匹配committee数据
    committee_matches = []
    for _, row in df.iterrows():
        bill_number = row['Bill Number']
        bill_name = row['Bill Name']
        committee_name = clean_text(row['Committee'])

        # 寻找匹配的committee
        matched_committee = committee_data.get(committee_name, None)

        if matched_committee:
            committee_matches.append({
                "Bill Number": bill_number,
                "Bill Name": bill_name,
                "Committee": {
                    "Committee": committee_name,
                    "Chair": matched_committee.get("Chair"),
                    "Ranking Member": matched_committee.get("Ranking Member")
                }
            })
        else:
            print(f"Committee not found: {committee_name}")

    # 保存匹配结果到文件
    save_json_file('caucus_matches.json', caucus_matches)
    save_json_file('committee_matches.json', committee_matches)


def update_committee_matches(file_path, profiles):
    committee_matches = load_json_file(file_path)
    for entry in committee_matches:
        bill_number = entry.get("Bill Number")
        committee_info = entry.get("Committee", {})
        chair_name = committee_info.get("Chair")
        ranking_member_name = committee_info.get("Ranking Member")

        for person_name in [chair_name, ranking_member_name]:
            if person_name in profiles:
                profile = profiles[person_name]
                records_fields = ['UnusedVotingRecords', 'CosponsoredBills', 'VotingRecord', 'SponsoredBills']
                for field in records_fields:
                    if field in profile:
                        for record in profile[field]:
                            if record.get("Bill Number") == bill_number:
                                if field not in entry:
                                    entry[field] = []
                                entry[field].append(record)
    save_json_file(file_path, committee_matches)


def update_caucus_matches(file_path, profiles):
    caucus_matches = load_json_file(file_path)
    for entry in caucus_matches:
        bill_number = entry.get("Bill Number")
        caucus_info = entry.get("Caucus", {})
        members = caucus_info.get("Members", [])

        for person_name in members:
            clean_person_name = person_name.split('(')[0].strip()
            if clean_person_name in profiles:
                profile = profiles[clean_person_name]
                records_fields = ['UnusedVotingRecords', 'CosponsoredBills', 'VotingRecord', 'SponsoredBills']
                for field in records_fields:
                    if field in profile:
                        for record in profile[field]:
                            if record.get("Bill Number") == bill_number:
                                if field not in entry:
                                    entry[field] = []
                                entry[field].append(record)
    save_json_file(file_path, caucus_matches)


def process_committee_json(input_file, output_file):
    # 读取输入的 JSON 文件
    with open(input_file, 'r') as f:
        data_list = json.load(f)

    # 处理每个数据项
    for data in data_list:
        # 获取委员会的主席和排名成员名字
        committee_chair = data["Committee"]["Chair"]
        committee_ranking_member = data["Committee"]["Ranking Member"]

        # 初始化空的投票记录
        data["Committee"]["Chair Voting Records"] = []
        data["Committee"]["Ranking Member Voting Records"] = []

        # 定义要遍历的字段
        fields_to_check = ["UnusedVotingRecords", "CosponsoredBills", "SponsoredBills", "VotingRecord"]

        # 遍历并匹配
        for field in fields_to_check:
            if field in data:
                records = data[field]
                updated_records = []
                for record in records:
                    first_name = record.get("First Name", "").strip()
                    last_name = record.get("Last Name", "").strip()
                    vote = record.get("Vote", "")

                    # 检查是否匹配到主席
                    if committee_chair in first_name:
                        data["Committee"]["Chair Voting Records"].append({
                            "First Name": first_name,
                            "Last Name": last_name,
                            "Vote": vote
                        })
                    # 检查是否匹配到排名成员
                    elif committee_ranking_member in first_name:
                        data["Committee"]["Ranking Member Voting Records"].append({
                            "First Name": first_name,
                            "Last Name": last_name,
                            "Vote": vote
                        })
                    else:
                        updated_records.append(record)

                # 更新原始字段
                data[field] = updated_records

        # 删除处理后的记录
        for field in fields_to_check:
            if field in data:
                del data[field]

    # 保存处理后的数据到新的 JSON 文件
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)


def process_caucus_json(input_file, output_file):
    # 读取输入的 JSON 文件
    with open(input_file, 'r') as f:
        data_list = json.load(f)

    for data in data_list:
        # 获取委员会的名称和成员
        caucus_name = data["Caucus"]["Caucus"]
        caucus_members = data["Caucus"]["Members"]

        # 初始化空的投票记录
        data["Caucus"]["Caucus Voting Records"] = []

        # 定义要遍历的字段
        fields_to_check = ["UnusedVotingRecords", "CosponsoredBills", "SponsoredBills", "VotingRecord"]

        # 用于存储临时记录
        temp_records = {}

        # 遍历并收集记录
        for field in fields_to_check:
            if field in data:
                records = data[field]
                for record in records:
                    first_name = record.get("First Name", "").strip()
                    last_name = record.get("Last Name", "").strip()
                    vote = record.get("Vote", "")

                    if first_name:
                        if first_name not in temp_records:
                            temp_records[first_name] = {"Last Name": "", "Vote": ""}

                        if vote:
                            temp_records[first_name]["Vote"] = vote
                        if last_name:
                            temp_records[first_name]["Last Name"] = last_name

        # 匹配记录并填充到 "Caucus Voting Records"
        for member in caucus_members:
            member_name = member.split('(')[0].strip()  # 只取名字部分，去掉党派信息
            if member_name in temp_records:
                data["Caucus"]["Caucus Voting Records"].append({
                    "First Name": member_name,
                    "Last Name": temp_records[member_name]["Last Name"],
                    "Vote": temp_records[member_name]["Vote"]
                })

        # 删除处理后的记录字段
        for field in fields_to_check:
            if field in data:
                del data[field]

    # 保存处理后的数据到新的 JSON 文件
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)


def main():
    personal_profiles_folder = r'E:\PycharmProjects\Legislators\data\profiles\profiles244'
    csv_filename = 'caucus_committee.csv'
    caucus_json_filename = 'caucus_data.json'
    committee_json_filename = 'committee_data.json'
    committee_matches_file = 'committee_matches.json'
    caucus_matches_file = 'caucus_matches.json'
    committee_output_file = 'committee_match.json'
    caucus_output_file = 'caucus_match.json'

    profiles = load_personal_profiles(personal_profiles_folder)

    # 处理 CSV 文件
    process_csv(csv_filename, caucus_json_filename, committee_json_filename)

    # 更新 committee_matches.json 和 caucus_matches.json 文件
    update_committee_matches(committee_matches_file, profiles)
    update_caucus_matches(caucus_matches_file, profiles)
    process_committee_json(committee_matches_file, committee_output_file)
    process_caucus_json(caucus_matches_file, caucus_output_file)

    print("委员会匹配结果保存在", committee_output_file)
    print("小组匹配结果保存在", caucus_output_file)


if __name__ == "__main__":
    main()

# 读取JSON文件
with open('caucus_match.json', 'r') as file:
    data = json.load(file)

# 确保data是一个列表
if isinstance(data, list):
    for item in data:
        # 提取党派信息
        members = item.get("Caucus", {}).get("Members", [])
        party_dict = {}

        for member in members:
            # 提取名字和党派
            name, party = member.rsplit('(', 1)
            party = party.rstrip(')')
            full_name = name.strip()
            party_dict[full_name] = party

        # 更新投票记录中的党派信息
        voting_records = item.get("Caucus", {}).get("Caucus Voting Records", [])

        for record in voting_records:
            full_name = record.get("First Name", "").strip()
            if full_name in party_dict:
                record["Last Name"] = party_dict[full_name]

    # 写回JSON文件
    with open('caucus_match.json', 'w') as file:
        json.dump(data, file, indent=4)

    print("更新完毕!")
else:
    print("读取的数据不是列表类型，请检查JSON文件的结构。")
