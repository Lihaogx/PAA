import os
import json
import shutil
import random
import string


def add_name_field_to_json_files(directory):
    # Iterate through files in directory
    for filename in os.listdir(directory):
        if filename.endswith("_profile.json"):
            file_path = os.path.join(directory, filename)

            # Extract Name field from filename
            name = filename.replace("_profile.json", "")

            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Add Name field at beginning of file
            data = {"Name": name, **data}

            # Write back to JSON file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Updated {filename} with Name: {name}")


# Party classification
class ProfileOrganizer:
    def __init__(self, profile_folder, republican_folder, democratic_folder):
        self.profile_folder = profile_folder
        self.republican_folder = republican_folder
        self.democratic_folder = democratic_folder

    def organize_profiles(self):
        # Create target folders if they don't exist
        os.makedirs(self.republican_folder, exist_ok=True)
        os.makedirs(self.democratic_folder, exist_ok=True)

        # Iterate through each file in profile folder
        for filename in os.listdir(self.profile_folder):
            if filename.endswith(".json"):
                file_path = os.path.join(self.profile_folder, filename)

                # Read JSON file
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # Get political party information
                political_party = data.get("Profile", {}).get("Personal Details", {}).get("Personal details", {}).get(
                    "Political party", "")

                # Copy file to appropriate folder based on political party
                if "Republican" in political_party:
                    shutil.copy(file_path, os.path.join(self.republican_folder, filename))
                elif "Democratic" in political_party:
                    shutil.copy(file_path, os.path.join(self.democratic_folder, filename))


# Name swapping
class NameSwapper:
    def __init__(self, republican_folder, democratic_folder):
        self.republican_folder = republican_folder
        self.democratic_folder = democratic_folder

    def load_profiles(self, folder):
        profiles = []
        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                file_path = os.path.join(folder, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    profiles.append((file_path, data))
        return profiles

    def extract_names(self, profiles):
        names = []
        for _, profile in profiles:
            name = profile.get('Name', '')
            if name:
                names.append(name)
        return names

    def replace_names(self, profiles, new_names):
        new_profiles = []
        index = 0
        for file_path, profile in profiles:
            new_profile = profile.copy()
            if index < len(new_names):
                new_name = new_names[index]
                new_profile['Name'] = new_name
                new_profiles.append((file_path, new_profile))
            index += 1
        return new_profiles

    def save_profiles(self, profiles, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
        for file_path, profile in profiles:
            filename = os.path.basename(file_path)
            new_file_path = os.path.join(folder, filename)
            with open(new_file_path, 'w', encoding='utf-8') as file:
                json.dump(profile, file, indent=4)

    def swap_names(self):
        # Load all profile files
        republican_profiles = self.load_profiles(self.republican_folder)
        democratic_profiles = self.load_profiles(self.democratic_folder)

        # Extract names
        republican_names = self.extract_names(republican_profiles)
        democratic_names = self.extract_names(democratic_profiles)

        # Randomly shuffle names
        random.shuffle(republican_names)
        random.shuffle(democratic_names)

        # Swap names
        updated_republican_profiles = self.replace_names(republican_profiles, democratic_names)
        updated_democratic_profiles = self.replace_names(democratic_profiles, republican_names)

        # Save updated profile files to new folders
        self.save_profiles(updated_republican_profiles, "new_" + self.republican_folder)
        self.save_profiles(updated_democratic_profiles, "new_" + self.democratic_folder)

        print("Names have been successfully exchanged between Republican and Democrat profiles.")


class ProfileAnonymizer:
    def __init__(self, profile_folder, modified_profile_folder):
        self.profile_folder = profile_folder
        self.modified_profile_folder = modified_profile_folder

    def generate_random_name(self, length=5):
        """Generate random uppercase string of specified length"""
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

    def anonymize_profiles(self):
        # Ensure new folder exists
        os.makedirs(self.modified_profile_folder, exist_ok=True)

        # Iterate through each file in profile folder
        for filename in os.listdir(self.profile_folder):
            if filename.endswith('_profile.json'):
                # Get file path
                file_path = os.path.join(self.profile_folder, filename)

                # Read JSON file
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # Generate random name
                random_name = self.generate_random_name()

                data['Name'] = random_name

                # Write to new folder
                modified_file_path = os.path.join(self.modified_profile_folder, filename)
                with open(modified_file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

        print("Anonymization completed!")


# Usage example
# Specify folder paths
directory = 'profiles_Sponsor'
add_name_field_to_json_files(directory)

# organizer = ProfileOrganizer("profiles0.2", "sampled_republican", "sampled_democratic")
# organizer.organize_profiles()
#
# swapper = NameSwapper("sampled_republican", "sampled_democratic")
# swapper.swap_names()
#
# anonymizer = ProfileAnonymizer("profiles0.2","anonymous0.2")
# anonymizer.anonymize_profiles()
