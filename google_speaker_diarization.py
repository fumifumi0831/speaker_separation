import os
from google.cloud import speech_v1p1beta1 as speech

def transcribe_file_with_speaker_diarization(
    audio_file_path, min_speaker_count=2, max_speaker_count=6
):
    """
    Google Cloud Speech-to-Text APIを使用して、オーディオファイルの文字起こしと話者分離を行う関数
    
    Parameters:
        audio_file_path (str): 処理するオーディオファイルのパス
        min_speaker_count (int): 想定される最小話者数
        max_speaker_count (int): 想定される最大話者数
    
    Returns:
        dict: 話者ごとに分けられた文字起こし結果
    """
    
    # Google Cloud SDKの認証（環境変数 GOOGLE_APPLICATION_CREDENTIALS で設定するか、
    # explicit_credentials = service_account.Credentials.from_service_account_file('path/to/key.json')
    # client = speech.SpeechClient(credentials=explicit_credentials) として認証する）
    client = speech.SpeechClient()
    
    # オーディオファイルの読み込み
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
    
    # オーディオファイルの設定
    audio = speech.RecognitionAudio(content=content)
    
    # 音声認識と話者分離の設定
    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=min_speaker_count,
        max_speaker_count=max_speaker_count,
    )
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,  # サンプリングレートに合わせて調整
        language_code="ja-JP",     # 日本語の場合（英語なら "en-US"）
        enable_automatic_punctuation=True,
        diarization_config=diarization_config,
        model="latest_long",  # 長時間音声向けモデル
    )
    
    print("音声認識処理を開始します...")
    response = client.recognize(config=config, audio=audio)
    
    # 結果の解析と話者ごとの整理
    result = response.results[-1]
    words_info = result.alternatives[0].words
    
    # 話者ごとに分けて保存
    speaker_transcripts = {}
    
    for word_info in words_info:
        speaker_tag = word_info.speaker_tag
        word = word_info.word
        
        if speaker_tag not in speaker_transcripts:
            speaker_transcripts[speaker_tag] = []
        
        speaker_transcripts[speaker_tag].append(word)
    
    # 話者ごとのテキストを結合
    for speaker, words in speaker_transcripts.items():
        speaker_transcripts[speaker] = " ".join(words)
    
    return speaker_transcripts


def main():
    # 使用例
    audio_file_path = "path/to/your/audio/file.wav"
    
    try:
        speaker_transcripts = transcribe_file_with_speaker_diarization(audio_file_path)
        
        print("\n=== 話者分離結果 ===")
        for speaker, transcript in speaker_transcripts.items():
            print(f"話者 {speaker}: {transcript}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
