import argparse
import json

import requests
from joblib import Parallel, delayed
from tqdm import tqdm

BASE_URL = "https://o9k5xn5546.execute-api.us-east-1.amazonaws.com/v1/archives/nuplan-v1.1/"


def login(username, password):
    headers = {
        "content-type": "application/x-amz-json-1.1",
        "x-amz-target": "AWSCognitoIdentityProviderService.InitiateAuth",
    }

    data = (
        '{"AuthFlow":"USER_PASSWORD_AUTH","ClientId":"7fq5jvs5ffs1c50hd3toobb3b9","AuthParameters":{"USERNAME":"'
        + username
        + '","PASSWORD":"'
        + password
        + '"},"ClientMetadata":{}}'
    )

    response = requests.post(
        "https://cognito-idp.us-east-1.amazonaws.com/",
        headers=headers,
        data=data,
    )

    token = json.loads(response.content)["AuthenticationResult"]["IdToken"]

    return token


def get_download_url(token, url):
    headers = {
        "authorization": "Bearer " + token,
    }

    params = {
        "region": "us",
        "project": "nuPlan",
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
    )
    download_url = json.loads(response.content)["url"]

    return download_url


def main():
    parser = argparse.ArgumentParser(description="Download nuPlan dataset")
    parser.add_argument("--username", required=True, help="Your username")
    parser.add_argument("--password", required=True, help="Your password")
    
    # Dataset selection arguments
    parser.add_argument("--test-set", action="store_true", help="Download test set (lidar + camera)")
    parser.add_argument("--train-set", action="store_true", help="Download train set (lidar + camera)")
    parser.add_argument("--val-set", action="store_true", help="Download val set (lidar + camera)")
    parser.add_argument("--mini-set", action="store_true", help="Download mini set (lidar + camera)")
    parser.add_argument("--maps", action="store_true", help="Download maps")
    parser.add_argument("--log-db", action="store_true", help="Download log database splits")
    
    # Sensor type selection
    parser.add_argument("--lidar-only", action="store_true", help="Download only lidar data")
    parser.add_argument("--camera-only", action="store_true", help="Download only camera data")
    
    # Download all if no specific dataset is selected
    parser.add_argument("--all", action="store_true", help="Download all datasets (default if no specific dataset selected)")
    
    args = parser.parse_args()

    # requests session
    with requests.Session() as s:
        # login and get auth token
        login_token = login(args.username, args.password)

        links = []
        
        # Determine what to download
        download_all = args.all or not any([
            args.test_set, args.train_set, args.val_set, args.mini_set, 
            args.maps, args.log_db
        ])
        
        # Determine sensor types to download
        download_lidar = not args.camera_only
        download_camera = not args.lidar_only
        
        # nuPlan Test Set
        if args.test_set or download_all:
            if download_lidar:
                links += [BASE_URL + f"sensor_blobs/test_set/nuplan-v1.1_test_lidar_{i}.zip" for i in range(12)]
            if download_camera:
                links += [BASE_URL + f"sensor_blobs/test_set/nuplan-v1.1_test_camera_{i}.zip" for i in range(12)]
        
        # nuPlan Train Set
        if args.train_set or download_all:
            if download_lidar:
                links += [BASE_URL + f"sensor_blobs/train_set/nuplan-v1.1_train_lidar_{i}.zip" for i in range(43)]
            if download_camera:
                links += [BASE_URL + f"sensor_blobs/train_set/nuplan-v1.1_train_camera_{i}.zip" for i in range(43)]
        
        # nuPlan Val Set
        if args.val_set or download_all:
            if download_lidar:
                links += [BASE_URL + f"sensor_blobs/val_set/nuplan-v1.1_val_lidar_{i}.zip" for i in range(12)]
            if download_camera:
                links += [BASE_URL + f"sensor_blobs/val_set/nuplan-v1.1_val_camera_{i}.zip" for i in range(12)]
        
        # Maps
        if args.maps or download_all:
            links += [BASE_URL + "nuplan-maps-v1.0.zip"]
        
        # Mini Set
        if args.mini_set or download_all:
            # Mini Split
            links += [BASE_URL + "nuplan-v1.1_mini.zip"]
            # Mini Sensors
            if download_lidar:
                links += [BASE_URL + f"sensor_blobs/mini_set/nuplan-v1.1_mini_lidar_{i}.zip" for i in range(9)]
            if download_camera:
                links += [BASE_URL + f"sensor_blobs/mini_set/nuplan-v1.1_mini_camera_{i}.zip" for i in range(9)]
        
        # Log DB splits
        if args.log_db or download_all:
            # Log DB Train Splits
            links += [
                BASE_URL + f"nuplan-v1.1_train_{city}.zip"
                for city in [
                    "boston",
                    "pittsburgh",
                    "singapore",
                    "vegas_1",
                    "vegas_2",
                    "vegas_3",
                    "vegas_4",
                    "vegas_5",
                    "vegas_6",
                ]
            ]
            # Log DB Val Splits
            links += [BASE_URL + "nuplan-v1.1_val.zip"]
            # Log DB Test Splits
            links += [BASE_URL + "nuplan-v1.1_test.zip"]

        print(f"다운로드할 파일 수: {len(links)}")
        
        if len(links) == 0:
            print("다운로드할 파일이 없습니다.")
            return

        download_links = Parallel(n_jobs=12)(delayed(get_download_url)(login_token, link) for link in tqdm(links))

        # write download links to file
        with open("download_links.txt", "w") as f:
            for link in download_links:
                f.write(link + "\n")


if __name__ == "__main__":
    main()
