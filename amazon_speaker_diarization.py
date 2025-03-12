import boto3
import json
import time
import uuid
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

def transcribe_with_speaker_diarization(audio_file_uri, language_code='ja-JP', max_speakers=10):
    """
    Amazon Transcribeを使用して、オーディオファイルの文字起こしと話者分離を行う関数
    
    Parameters:
        audio_file_uri (str): S3上のオーディオファイルURI (s3://bucket-name/file-name.mp3)
        language_code (str): 言語コード（日本語の場合は'ja-JP'）
        max_speakers (int): 想定される最大話者数
    
    Returns:
        dict: 話者ごとに分けられた文字起こし結果
    """
    # Amazon Transcribeクライアントの初期化
    transcribe = boto3.client('transcribe')
    
    # ジョブ名の生成（一意の名前である必要がある）
    job_name = f"speaker-diarization-{str(uuid.uuid4())}"
    
    # 入力ファイルの形式を取得
    parsed_url = urlparse(audio_file_uri)
    file_format = parsed_url.path.split('.')[-1].lower()
    
    # サポートされているフォーマットかチェック
    supported_formats = ['mp3', 'mp4', 'wav', 'flac', 'ogg', 'amr', 'webm']
    if file_format not in supported_formats:
        raise ValueError(f"サポートされていないフォーマットです: {file_format}. サポートされているフォーマット: {supported_formats}")
    
    print(f"文字起こしジョブを開始します: {job_name}")
    
    # 文字起こしジョブの開始
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': audio_file_uri},
        MediaFormat=file_format,
        LanguageCode=language_code,
        Settings={
            'ShowSpeakerLabels': True,
            'MaxSpeakerLabels': max_speakers
        }
    )
    
    # ジョブの完了を待機
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("処理中...")
        time.sleep(30)
    
    # ジョブが失敗した場合
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
        raise Exception(f"文字起こしジョブが失敗しました: {status['TranscriptionJob']['FailureReason']}")
    
    # 結果の取得
    transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    
    # 結果のダウンロードと解析
    import urllib.request
    response = urllib.request.urlopen(transcript_uri)
    data = json.loads(response.read().decode('utf-8'))
    
    # 話者ごとの発言を整理
    speaker_transcripts = {}
    
    if 'speaker_labels' in data['results']:
        speaker_segments = data['results']['speaker_labels']['segments']
        items = data['results']['items']
        
        # 各セグメント内の話者と発言内容を対応付け
        for segment in speaker_segments:
            speaker_label = segment['speaker_label']
            start_time = float(segment['start_time'])
            end_time = float(segment['end_time'])
            
            if speaker_label not in speaker_transcripts:
                speaker_transcripts[speaker_label] = []
            
            # セグメント内の単語を特定
            segment_words = []
            for item in items:
                # 単語（発音）アイテムのみを対象
                if 'start_time' not in item:
                    continue
                
                item_start_time = float(item['start_time'])
                item_end_time = float(item['end_time'])
                
                # セグメントの時間範囲内にある単語を追加
                if item_start_time >= start_time and item_end_time <= end_time:
                    if 'alternatives' in item and len(item['alternatives']) > 0:
                        segment_words.append(item['alternatives'][0]['content'])
            
            # セグメント内の単語を連結して追加
            if segment_words:
                speaker_transcripts[speaker_label].append(' '.join(segment_words))
    
    # 話者ごとの発言をまとめる
    for speaker, segments in speaker_transcripts.items():
        speaker_transcripts[speaker] = ' '.join(segments)
    
    # 完了したジョブの削除（オプション）
    try:
        transcribe.delete_transcription_job(TranscriptionJobName=job_name)
    except Exception as e:
        print(f"ジョブの削除中にエラーが発生しました: {e}")
    
    return speaker_transcripts


def main():
    # 使用例（事前にS3にファイルをアップロードする必要があります）
    audio_file_uri = "s3://your-bucket-name/your-audio-file.mp3"
    
    try:
        # AWS認証情報は環境変数、AWSプロファイル、またはIAMロールから取得されます
        # 必要に応じて、boto3.client('transcribe', aws_access_key_id='KEY', aws_secret_access_key='SECRET', region_name='REGION')を使用
        
        speaker_transcripts = transcribe_with_speaker_diarization(audio_file_uri)
        
        print("\n=== 話者分離結果 ===")
        for speaker, transcript in speaker_transcripts.items():
            print(f"{speaker}: {transcript}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
