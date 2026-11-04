---
name: infra-architecture
description: このプロジェクトの Terraform インフラ設計指針（運用の前提、層構成と置き場所の判断、層をまたぐ約束、意図した差分・決定済みの事項、書き方の規約、Docker での静的解析、サービスごとの確認項目）。`infra/` 配下の Terraform コードや Terraform を実行する CI のワークフローを新規作成・編集する前、およびそのレビュー時に必ず参照する。
disable-model-invocation: false
---

# インフラ設計指針

<!--
  テンプレート: プロジェクトに合わせて書き換えること。
  - 下記の各節の「TODO」をプロジェクトの実態に置き換える
  - 不要な節は削除してよい。量が増えたら層やサービスごとに references/ へ分けてよい（分けた場合は末尾の「参照ファイル」に一覧を書く）
  - 書き終えたら description もプロジェクト固有のキーワード（クラウド名・主要サービス名など）を含めて具体化すると、自動参照されやすくなる
  - 書き終えたら、.claude/settings.json の permissions.deny から "Agent(terraform-infra-reviewer)" を消すと、レビュアーが起動するようになる
-->

インフラは TODO（例: `infra/terraform/`）の Terraform で管理する。仕様は TODO（仕様書のパス）、運用手順は TODO（例: `infra/README.md`）にある。この指針と食い違う場合は仕様書を正とし、食い違いを指示者に報告する。

## 運用の前提

- plan / apply の方法: TODO（例: GitHub Actions の手動実行だけで行う。ワークフロー名、承認の仕組み）
- ローカルや開発エージェントから `terraform apply` / `destroy`、クラウドの CLI での変更操作は行わない
- Terraform と provider の版: TODO（例: Terraform v1.11 以上、provider は全層で同じ版にそろえ、各層の `.terraform.lock.hcl` をコミットする）
- state の置き場所とロック: TODO
- Terraform の管理外のもの（手動で作ったもの）: TODO（例: state 用のバケット、DNS のゾーン。`data` で参照する）
- 秘密情報の扱い: TODO（例: 値は Terraform に書かず、秘密情報の入れ物だけを作り、値は指示者がコンソールで設定する）
- `.claude/settings.json` の拒否設定により、名前に `secret` を含むファイルはエージェントが読めない。秘密情報を扱うリソースのファイル名に `secret` を含めると、実装・レビューで中身を確かめられなくなる点に注意する

## 層構成

TODO: state を分けている単位（層）と適用順を書く。分けていなければ節ごと削除する。

| 層 | 置くもの | 性格 |
| -- | -------- | ---- |
| TODO（例: `global`） | 例: CI 用の権限、コンテナのレジストリ | アカウント共有の土台。壊すと CI からクラウドに入れなくなる |
| TODO（例: `<環境>-base`） | 例: ネットワーク、DB、秘密情報、データ用の保存先 | 消したくない永続層。destroy しない |
| TODO（例: `<環境>`） | 例: ロードバランサ、計算資源、証明書、DNS レコード | いつでも作り直してよい層 |

適用順: TODO（例: `global` → `staging-base` → `staging`）

### 置き場所の判断

- destroy・作り直しで失われて困るもの（データ、手動で入れた秘密情報、消えると公開範囲が広がる制限、他層から参照される土台）→ 永続的な層
- いつでも作り直せるもの（計算資源、ロードバランサ、証明書、DNS レコード）→ 環境本体
- 複数環境で共有するもの、CI の権限 → 共有の層
- 通信の許可ルールは、許可する側のリソースがある層で管理する

## 層をまたぐ約束

TODO: プロジェクトの実態に合わせて足す・消す。

1. **他の層から読まれている outputs は約束**。名前変更・削除・意味の変更は読む側を壊す。変える場合は新しい output を追加 → 読む側を切り替え → 古い output を削除、の順で行う
2. **module の変更はその module を使う全ての層に効く**。`grep -rn 'modules/<名前>' infra/` で使っている層を洗い出し、層ごとの基準で影響を確かめる
3. **新しい種類のリソースを使い始めたら、plan・apply を行うロールの権限を確かめる**。足りないと plan が権限エラーで止まる。権限を足す層を先に apply する
4. **CI のデプロイ用の権限が名前の規則に依存している場合は、名前を変えるときに権限とワークフローも合わせて直す**。TODO: 名前の規則
5. **対になっている環境（例: staging と production）は片方だけを直さない**。意図した差分は次節の表にあるもののみ

## 意図した差分・決定済みの事項

以下は仕様書で決まっているため、変更しない限り指摘の対象にしない。

| 事項 | 内容 |
| ---- | ---- |
| TODO（例: NAT ゲートウェイなし） | TODO（例: コスト優先の決定。代わりにどう守っているか） |

## 書き方の規約

- 1 つの層・module のファイル構成は `main.tf` / `variables.tf` / `outputs.tf`（層は加えて `providers.tf` / `backend.tf`）。量が多い場合は役割で分けてよい
- variable と output には必ず `description` を書く。variable には `type` を付け、取り得る値が決まっているもの・形式があるものは `validation` を付ける。秘密情報は `sensitive = true`
- 名前の付け方・タグの付け方: TODO（例: `<プロジェクト>-<環境>` で始める。共通のタグは provider の `default_tags` で付ける）
- 環境ごとの値の渡し方: TODO（例: variable の `default` に書き、`*.tfvars` は git 管理外。CI の秘密情報から `TF_VAR_*` で渡す）
- コメントは「なぜそうしたか」（決定事項・制約・層をまたぐ理由）だけを書く。自明なコメントや経緯は書かない
- 状態を持つリソース（DB・秘密情報・データの入った保存先）に、置き換え（replace）を引き起こす変更を入れない。どうしても必要な場合は、データの移し方と手順を仕様書に書いて指示者の了承を得てから行う

## 静的解析（Docker で実行する）

ローカルにツールはインストールしない。リポジトリ直下で実行する。作業場所を汚さないよう、ソースは読み取り専用でマウントし、コンテナ内にコピーしてから実行する。

TODO: Terraform のディレクトリ、イメージの版、層の名前をプロジェクトに合わせる。イメージの版は固定する。

```bash
# 書式チェックと構文チェック（<env> は層の名前）
docker run --rm -v "$PWD/infra/terraform:/src:ro" --entrypoint sh hashicorp/terraform:<版> -c \
  'terraform fmt -check -recursive /src && cp -r /src /work && cd /work/envs/<env> && terraform init -backend=false -input=false >/dev/null && terraform validate'

# tflint（クラウドのルールセットを使う場合は、このスキルのフォルダに .tflint.hcl を置き、--config で渡す）
docker run --rm -v "$PWD/infra/terraform:/src:ro" --entrypoint sh ghcr.io/terraform-linters/tflint:<版> -c \
  'cp -r /src /work && cd /work && tflint --init >/dev/null && tflint --recursive --format compact'

# Trivy（設定ミスの検出）
docker run --rm -v "$PWD/infra/terraform:/src:ro" aquasec/trivy:<版> config --quiet --severity HIGH,CRITICAL /src

# Checkov（設定ミスの検出。Trivy より観点が広く検出も多い）
docker run --rm -v "$PWD/infra/terraform:/src:ro" bridgecrew/checkov:<版> -d /src --framework terraform --quiet --compact
```

- 差分で新しく増えた検出・差分の行に関わる検出だけを指摘の対象にし、既存の検出は件数だけをまとめる
- 指摘しない検出（決定済みの事項によるもの・誤検知）: TODO（例: `<ツール> <検出ID>`（理由））
- `terraform plan` はクラウドの認証情報が必要なためエージェントからは実行しない。plan の結果は指示者に貼ってもらう

## サービスごとの確認項目

TODO: 使っているクラウドのサービスごとに、確認する項目を書く。根拠にするベストプラクティス（例: AWS なら AWS Security Hub の基礎的ベストプラクティス（FSBP）と CIS AWS Foundations Benchmark）があれば、項目番号付きで書く。

- TODO（例: ネットワーク）: 例: 公開してよい通信口だけが開いているか
- TODO（例: DB）: 例: 暗号化・バックアップ・削除保護・公開されていないこと
- TODO（例: 保存先）: 例: 一般公開の遮断・暗号化・バージョニング
- TODO（例: 権限）: 例: 必要な操作とリソースだけに絞っているか。CI のロールは使う場所を限定しているか

## 参照ファイル

TODO: references/ に分けた場合は、ファイルと読む場面の一覧を書く。分けていなければ節ごと削除する。
