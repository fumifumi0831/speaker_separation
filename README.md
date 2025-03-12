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

プロジェクト固有の環境変数を設定するために、`.env`ファイルを使用します：

1. `.env.example`ファイルを`.env`にコピーします：

```bash
cp .env.example .env
```

2. `.env`ファイルを編集して、認証情報を設定します：

```
# Google Cloud Speech-to-Text認証情報
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-project-credentials.json

# Google Cloud Storage設定
GCS_BUCKET_NAME=your-bucket-name

# Amazon Transcribe認証情報
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=your-region
```

この方法により、環境変数はこのプロジェクトのみで有効になり、システム全体には影響しません。

#### Google Cloud Speech-to-Text

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Speech-to-Text APIを有効化
3. サービスアカウントキー（JSON形式）を作成・ダウンロード
4. `.env`ファイルに認証情報のパスを設定

#### Google Cloud Storage（大きな音声ファイル用）

1. [Google Cloud Console](https://console.cloud.google.com/)でCloud Storage APIを有効化
2. バケットを作成するか、既存のバケット名を`.env`ファイルに設定
3. サービスアカウントに適切な権限（Storage Admin等）を付与

#### Amazon Transcribe

1. [AWS マネジメントコンソール](https://aws.amazon.com/console/)でAWS IAM設定
2. 適切な権限（Amazon Transcribe、S3アクセス）を持つIAMユーザーを作成
3. アクセスキーとシークレットキーを取得
4. `.env`ファイルに認証情報を設定

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

# 結果をファイルに保存（オプション）
from google_speaker_diarization import save_results_to_file
# テキスト形式で保存
output_file = save_results_to_file(speaker_results, audio_file_path)
# または JSON形式で保存
output_file = save_results_to_file(speaker_results, audio_file_path, output_format="json")
```

#### 結果の保存

話者分離の結果は、以下の方法で保存できます：

1. **テキスト形式（デフォルト）**：
   - 各話者の発言が読みやすいテキスト形式で保存されます
   - ファイル名: `{元のファイル名}_{タイムスタンプ}_results.txt`

2. **JSON形式**：
   - 構造化されたデータとして保存され、他のプログラムでの利用に適しています
   - ファイル名: `{元のファイル名}_{タイムスタンプ}_results.json`

結果は `speaker_separation_results` ディレクトリに保存されます。

#### 大きな音声ファイルの処理

10MB以上の音声ファイルは自動的にGoogle Cloud Storageを使用して処理されます。明示的にGCSを使用する場合は以下のように指定できます：

```python
from google_speaker_diarization import transcribe_gcs_with_speaker_diarization

# GCSを使用して大きな音声ファイルを処理
audio_file_path = "path/to/your/large_audio.wav"
speaker_results = transcribe_gcs_with_speaker_diarization(
    audio_file_path,
    min_speaker_count=2,
    max_speaker_count=6,
    bucket_name="your-bucket-name",  # オプション（.envに設定している場合は不要）
    timeout=1800  # タイムアウト時間（秒）、デフォルトは600秒（10分）
)

# 結果の表示
for speaker, transcript in speaker_results.items():
    print(f"話者 {speaker}: {transcript}")
```

長い音声ファイル（例：30分以上）を処理する場合は、タイムアウト時間を適切に設定してください：
- 30分の音声: `timeout=1800`（30分）
- 60分の音声: `timeout=3600`（60分）
- 120分の音声: `timeout=7200`（120分）

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
- ペイロードサイズエラー (`400 Request payload size exceeds the limit: 10485760 bytes`): 
  - 10MB以上の音声ファイルは自動的にGoogle Cloud Storageを使用して処理されます
  - GCS_BUCKET_NAME環境変数が正しく設定されているか確認してください
  - サービスアカウントにCloud Storageへのアクセス権があるか確認してください
- タイムアウトエラー (`Operation did not complete within the designated timeout`):
  - 長い音声ファイルの処理には時間がかかります
  - より長いタイムアウト時間を指定してください：
    ```python
    # 例: 30分（1800秒）のタイムアウトを設定
    transcribe_file_with_speaker_diarization(audio_file_path, timeout=1800)
    # または直接GCS関数を使用
    transcribe_gcs_with_speaker_diarization(audio_file_path, timeout=1800)
    ```

### Google Cloud Storage

- アクセス権限エラー (`403 speeach-separate@... does not have storage.buckets.get access`):
  1. Google Cloud Consoleの[IAMと管理 > IAM](https://console.cloud.google.com/iam-admin/iam)に移動
  2. サービスアカウントを見つけて編集
  3. 以下のいずれかのロールを追加：
     - `Storage 管理者` (Storage Admin) - すべてのStorage操作の権限
     - または最小権限として:
       - `Storage オブジェクト管理者` (Storage Object Admin)
       - `Storage バケット閲覧者` (Storage Buckets Viewer)
  4. 既存のバケットが存在することを確認し、`.env`ファイルに正しいバケット名を設定

### Amazon Transcribe

- S3アクセスエラー: IAMポリシーでS3バケットへのアクセス権があるか確認
- ジョブ失敗: サポートされている音声フォーマットを使用しているか確認

## ライセンス

MIT

## 貢献

Pull requestやIssueは歓迎します。大きな変更を加える前に、まずIssueで議論してください。
