# 話者分離（Speaker Diarization）実装

このリポジトリは、音声ファイルから複数の話者を識別し、話者ごとの文字起こしを行う「話者分離（Speaker Diarization）」の実装例を提供します。企業のセキュリティ要件に適合するよう、商用APIを使用したアプローチを採用しています。

## 対応サービス

1. Google Cloud Speech-to-Text
2. Amazon Transcribe

## 前提条件

- Python 3.8以上
- 各クラウドプロバイダーのアカウントと認証情報

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/fumifumi0831/speaker_separation.git
cd speaker_separation
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 認証情報の設定

#### Google Cloud Speech-to-Text

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Speech-to-Text APIを有効化
3. サービスアカウントキー（JSON形式）を作成・ダウンロード
4. 環境変数の設定：

```bash
# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-project-credentials.json"

# Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\\path\\to\\your-project-credentials.json"
```

#### Amazon Transcribe

1. [AWS マネジメントコンソール](https://aws.amazon.com/console/)でAWS IAM設定
2. 適切な権限（Amazon Transcribe、S3アクセス）を持つIAMユーザーを作成
3. アクセスキーとシークレットキーを取得
4. AWS認証情報の設定：

```bash
# AWS CLIのインストール
pip install awscli

# 認証情報の設定
aws configure
```

または環境変数として：

```bash
# Linux/Mac
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="your-region"

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="your-region"
```

## 使用方法

### Google Cloud Speech-to-Text

```python
from google_speaker_diarization import transcribe_file_with_speaker_diarization

# ローカルの音声ファイルを処理
audio_file_path = "path/to/your/audio.wav"  # 16kHzのWAVファイル推奨
speaker_results = transcribe_file_with_speaker_diarization(
    audio_file_path, 
    min_speaker_count=2, 
    max_speaker_count=6
)

# 結果の表示
for speaker, transcript in speaker_results.items():
    print(f"話者 {speaker}: {transcript}")
```

### Amazon Transcribe

Amazon TranscribeはS3上のファイルを処理するため、まずファイルをS3にアップロードする必要があります：

```python
import boto3
from amazon_speaker_diarization import transcribe_with_speaker_diarization

# S3にファイルをアップロード
s3 = boto3.client('s3')
bucket_name = 'your-bucket-name'
file_name = 'your-audio.mp3'
s3.upload_file('path/to/local/audio.mp3', bucket_name, file_name)

# S3のURIを構築
audio_uri = f"s3://{bucket_name}/{file_name}"

# 話者分離を実行
speaker_results = transcribe_with_speaker_diarization(
    audio_uri,
    language_code='ja-JP',
    max_speakers=10
)

# 結果の表示
for speaker, transcript in speaker_results.items():
    print(f"{speaker}: {transcript}")
```

## オーディオ形式のベストプラクティス

最適な結果を得るために、以下の推奨事項に従ってください：

1. **サンプリングレート**: 16kHz以上
2. **フォーマット**:
   - Google: LINEAR16 (WAV)、FLAC
   - Amazon: MP3、WAV、FLAC
3. **音質**:
   - クリアな音声（ノイズが少ないもの）
   - 各話者の音量レベルが均一
   - オーバーラップの少ない会話

## セキュリティ上の注意点

- API認証情報は環境変数または安全な方法で管理してください
- 本番環境ではIAMロールやサービスアカウントの権限を最小限に絞ってください
- センシティブな音声データを扱う場合は、各クラウドプロバイダーのデータ保持ポリシーを確認してください

## 料金

各サービスの料金体系は以下のリンクを参照してください：

- [Google Cloud Speech-to-Text の料金](https://cloud.google.com/speech-to-text/pricing)
- [Amazon Transcribe の料金](https://aws.amazon.com/transcribe/pricing/)

## トラブルシューティング

### Google Cloud Speech-to-Text

- 認証エラー: GOOGLE_APPLICATION_CREDENTIALS環境変数が正しく設定されているか確認
- 音声認識エラー: オーディオフォーマットとサンプリングレートを確認

### Amazon Transcribe

- S3アクセスエラー: IAMポリシーでS3バケットへのアクセス権があるか確認
- ジョブ失敗: サポートされている音声フォーマットを使用しているか確認

## ライセンス

MIT

## 貢献

Pull requestやIssueは歓迎します。大きな変更を加える前に、まずIssueで議論してください。
