# サンプルスクリプト: Google Cloud Speech-to-Textでの話者分離
# 実際のオーディオファイルと適切な認証情報が必要です

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_speaker_diarization import transcribe_file_with_speaker_diarization

def main():
    # オーディオファイルパスを指定
    audio_file_path = "../sample_data/conversation.wav"  # 自分のファイルパスに変更してください
    
    # 話者分離を実行
    try:
        print("Google Cloud Speech-to-Textによる話者分離を開始...")
        speaker_transcripts = transcribe_file_with_speaker_diarization(
            audio_file_path,
            min_speaker_count=2,
            max_speaker_count=4  # 想定される最大話者数に調整
        )
        
        # 結果の表示と保存
        print("\n=== 話者分離結果 ===")
        with open("google_results.txt", "w", encoding="utf-8") as f:
            for speaker, transcript in speaker_transcripts.items():
                output = f"話者 {speaker}: {transcript}"
                print(output)
                f.write(output + "\n")
        
        print("\n結果はgoogle_results.txtに保存されました")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
