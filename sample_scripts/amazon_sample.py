# サンプルスクリプト: Amazon Transcribeでの話者分離
# S3へのアクセスと適切な認証情報が必要です

import sys
import os
import boto3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amazon_speaker_diarization import transcribe_with_speaker_diarization

def main():
    # S3バケットとファイル名の設定
    bucket_name = "your-bucket-name"  # 自分のバケット名に変更
    file_name = "conversation.mp3"    # 自分のファイル名に変更
    local_file_path = "../sample_data/conversation.mp3"  # ローカルファイルパス
    
    # S3にファイルをアップロード
    try:
        print(f"S3 ({bucket_name})にファイルをアップロード中...")
        s3 = boto3.client('s3')
        s3.upload_file(local_file_path, bucket_name, file_name)
        print("アップロード完了")
        
        # S3のファイルURIを構築
        audio_uri = f"s3://{bucket_name}/{file_name}"
        
        # 話者分離を実行
        print("Amazon Transcribeによる話者分離を開始...")
        speaker_transcripts = transcribe_with_speaker_diarization(
            audio_uri,
            language_code='ja-JP',
            max_speakers=4  # 想定される最大話者数に調整
        )
        
        # 結果の表示と保存
        print("\n=== 話者分離結果 ===")
        with open("amazon_results.txt", "w", encoding="utf-8") as f:
            for speaker, transcript in speaker_transcripts.items():
                output = f"{speaker}: {transcript}"
                print(output)
                f.write(output + "\n")
        
        print("\n結果はamazon_results.txtに保存されました")
        
        # オプション: 処理が終わったS3のファイルを削除
        # s3.delete_object(Bucket=bucket_name, Key=file_name)
        # print(f"S3のファイル {file_name} を削除しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
