import pandas as pd
import json
import os
import re


# 原始数据读取
class ExcelToJsonExtractor:
    def __init__(self, excel_file_path, json_output_path):
        self.excel_file_path = excel_file_path
        self.json_output_path = json_output_path

    def load_excel(self):
        """加载Excel文件并提取right_json列的内容"""
        self.df = pd.read_excel(self.excel_file_path)
        self.right_json_list = self.df['right_json'].tolist()

    def extract_profiles(self):
        """将提取的right_json列内容转换为JSON格式"""
        self.profiles = []
        for item in self.right_json_list:
            self.profiles.append(json.loads(item))

    def save_to_json(self):
        """将提取的Profile信息保存到JSON文件中"""
        with open(self.json_output_path, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=4)

    def run(self):
        """执行所有步骤"""
        self.load_excel()
        self.extract_profiles()
        self.save_to_json()
        print(f'Profiles extracted and saved to {self.json_output_path}')


# # 运行
# excel_file_path = 'wiki.xlsx'
# json_output_path = 'wiki.json'
# extractor = ExcelToJsonExtractor(excel_file_path, json_output_path)
# extractor.run()


# Profile信息提取
class PersonalProcessor:
    def __init__(self, input_file, output_dir, extract_public_office=True, extract_personal_details=True,
                 extract_additional_info=True):
        self.input_file = input_file
        self.output_dir = output_dir
        self.extract_public_office = extract_public_office
        self.extract_personal_details = extract_personal_details
        self.extract_additional_info = extract_additional_info
        os.makedirs(self.output_dir, exist_ok=True)

    def sanitize_filename(self, filename):
        # 替换不允许的字符
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def clean_text(self, text):
        if isinstance(text, str):
            # 替换NBSP和ZWSP以及其他不需要的字符
            text = text.replace('\u00A0', ' ')  # NBSP
            text = text.replace('\u200B', '')  # ZWSP
            text = re.sub(r'\s+', ' ', text)  # 替换连续的空格为一个空格
            return text.strip()
        elif isinstance(text, dict):
            # 如果是字典，则递归处理每个值
            return {k: self.clean_text(v) for k, v in text.items()}
        elif isinstance(text, list):
            # 如果是列表，则递归处理每个元素
            return [self.clean_text(v) for v in text]
        else:
            return text

    def process_data(self):
        # 读取JSON文件
        with open(self.input_file, 'r', encoding='utf-8') as f:
            profiles = json.load(f)

        # 遍历
        for profile in profiles:
            for name, info in profile.items():
                # 初始化分类信息
                structured_info = {"Profile": {}}

                # 控制字段提取的参数
                if self.extract_public_office:
                    structured_info["Profile"]["Public Office"] = {}
                if self.extract_personal_details:
                    structured_info["Profile"]["Personal Details"] = {}
                if self.extract_additional_info:
                    structured_info["Profile"]["Additional Information"] = {}

                # 分界点为"Personal details"
                personal_details_found = False

                for key, value in info.items():
                    if key == "Personal details":
                        personal_details_found = True
                        if self.extract_personal_details:
                            # 清理个人详细信息字段
                            structured_info["Profile"]["Personal Details"][key] = self.clean_text(value)
                    elif personal_details_found:
                        if self.extract_additional_info:
                            # 清理附加信息字段
                            structured_info["Profile"]["Additional Information"][key] = self.clean_text(value)
                    else:
                        if self.extract_public_office:
                            # 清理公职信息字段
                            structured_info["Profile"]["Public Office"][key] = self.clean_text(value)

                # 生成安全的文件名
                safe_name = self.sanitize_filename(name)
                output_path = os.path.join(self.output_dir, f'{safe_name}_profile.json')

                # 保存为json文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(structured_info, f, ensure_ascii=False, indent=4)

        print("所有议员信息已成功保存到profile文件夹中。")


# 选区信息
class ProfileUpdater:
    def __init__(self, profile_folder, district_folder):
        self.profile_folder = profile_folder
        self.district_folder = district_folder
        self.district_files = os.listdir(district_folder)

    def extract_location(self, public_office_dict):
        for key in public_office_dict:
            match = re.search(r"Representativesfrom (.+?)'", key)
            if match:
                return match.group(1)
        return None

    def find_matching_district(self, location):
        """在district文件名中查找匹配的地点信息"""
        for district_file in self.district_files:
            if location in district_file:
                return district_file
        return None

    def update_profile(self, profile_file):
        """更新单个profile文件中的Public Office字段，插入匹配的district文件内容"""
        profile_path = os.path.join(self.profile_folder, profile_file)
        with open(profile_path, 'r', encoding='utf-8') as file:
            profile_data = json.load(file)

        # 提取Public Office字段中的地点信息
        public_office_dict = profile_data.get('Profile', {}).get('Public Office', {})
        location = self.extract_location(public_office_dict)

        if location:
            # 查找匹配的district文件
            matching_district_file = self.find_matching_district(location)
            if matching_district_file:
                district_path = os.path.join(self.district_folder, matching_district_file)
                with open(district_path, 'r', encoding='utf-8') as file:
                    district_data = json.load(file)

                # 插入匹配的district文件内容到Public Office字段
                for key in public_office_dict:
                    if f"Representativesfrom {location}" in key:
                        public_office_dict[key]["District Info"] = district_data
                        break

                # 将更新后的profile数据写回文件
                with open(profile_path, 'w', encoding='utf-8') as file:
                    json.dump(profile_data, file, indent=4, ensure_ascii=False)
                # print(f"Updated profile: {profile_file} with district data from: {matching_district_file}")

    def update_all_profiles(self):
        """更新所有profile文件"""
        for profile_file in os.listdir(self.profile_folder):
            self.update_profile(profile_file)


# 法案信息匹配
class ProfileMerger:
    def __init__(self, profile_folder, bill_profiles_folder, merge_fields, merge_ratios):
        self.profile_folder = profile_folder
        self.bill_profiles_folder = bill_profiles_folder
        self.merge_fields = merge_fields
        self.merge_ratios = merge_ratios

    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_json(self, file_path, data):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def standardize_name(self, name):
        # 去除多余的空格，并转换为统一格式
        return re.sub(r'\s+', ' ', name.strip()).lower()

    def find_matching_bill_file(self, profile_name):
        standardized_profile_name = self.standardize_name(profile_name)
        bill_profile_files = os.listdir(self.bill_profiles_folder)

        for bill_file in bill_profile_files:
            standardized_bill_name = self.standardize_name(bill_file.split('_profile')[0])
            if standardized_profile_name == standardized_bill_name:
                return bill_file
        return None

    def merge_profiles(self):
        profile_files = os.listdir(self.profile_folder)

        for profile_file in profile_files:
            profile_name = profile_file.split('_profile')[0]
            matching_bill_profile_file = self.find_matching_bill_file(profile_name)

            if matching_bill_profile_file:
                profile_path = os.path.join(self.profile_folder, profile_file)
                bill_profile_path = os.path.join(self.bill_profiles_folder, matching_bill_profile_file)

                profile_data = self.load_json(profile_path)
                bill_profile_data = self.load_json(bill_profile_path)

                # 清除合并字段中的原始数据
                for field in self.merge_fields:
                    if field in profile_data:
                        profile_data[field] = []
                    if field == 'VotingRecord':
                        profile_data['UnusedVotingRecords'] = []

                # 提取所需比例的投票数据
                for field in self.merge_fields:
                    if field in bill_profile_data and self.merge_ratios.get(field, 0) > 0:
                        data_to_merge = bill_profile_data[field]
                        num_items_to_merge = max(1, int(len(data_to_merge) * self.merge_ratios.get(field, 1)))

                        if num_items_to_merge > len(data_to_merge):
                            num_items_to_merge = len(data_to_merge)

                        data_to_merge = data_to_merge[::-1]
                        if field == 'VotingRecord':
                            profile_data[field] = data_to_merge[:num_items_to_merge]
                            profile_data['UnusedVotingRecords'] = data_to_merge[num_items_to_merge:]
                        else:
                            profile_data[field] = data_to_merge[:num_items_to_merge]

                self.save_json(profile_path, profile_data)


def main():
    # 个人信息
    profile_folder = 'profiles_Record'
    input_file = 'wiki.json'
    output_dir = profile_folder
    district_folder = 'district'
    bill_profiles_folder = 'bill_profiles'

    extract_public_office = True  # 是否提取公职信息
    extract_personal_details = True  # 是否提取个人详细信息
    extract_additional_info = False  # 是否提取附加信息
    merge_fields = ['CosponsoredBills', 'SponsoredBills', 'VotingRecord', 'UnusedVotingRecords']  # 法案提取列表
    # 法案提取比例
    merge_ratios = {
        'CosponsoredBills': 1,
        'SponsoredBills': 1,
        'VotingRecord': 0.2
    }
    # 初始化
    processor = PersonalProcessor(input_file, output_dir, extract_public_office, extract_personal_details,
                                  extract_additional_info)
    updater = ProfileUpdater(profile_folder, district_folder)
    merger = ProfileMerger(profile_folder, bill_profiles_folder, merge_fields, merge_ratios)
    # 运行
    processor.process_data()
    updater.update_all_profiles()
    merger.merge_profiles()


if __name__ == "__main__":
    main()
