# my-claude-setting

Claude Code のプロジェクト用設定（`.claude/`）を汎用化したテンプレート集です。
shucale_hub の `.claude/` をもとに、プロジェクト固有の内容（Rails / Flutter 固有のルール、起動・停止スキル、エージェントメモリ）を取り除いています。

## 構成

```
template/
├── CLAUDE.md                 # プロジェクト指示のテンプレート（TODO を書き換える）
├── .gitignore.claude         # プロジェクトの .gitignore に追記する内容
└── .claude/
    ├── settings.json         # 権限設定、レビュアーの ON/OFF、orchestrator をサブエージェントとして呼ばせない hook の登録
    ├── hooks/
    │   └── block-orchestrator-subagent.sh # orchestrator をサブエージェントとして起動しようとしたら拒否する
    ├── commands/
    │   └── spec.md                # /spec <テーマ> で spec-interview を開始する
    ├── agents/
    │   ├── orchestrator.md        # 司令塔。設計・判断・実装を行い、チェック・レビューを専門エージェントに任せる（メイン専用）
    │   ├── requirement-checker.md # 要求を満たしているかの検査
    │   ├── overview-checker.md    # 他機能・サービス全体への影響、既存の仕組みとの重複の検査
    │   ├── test-checker.md        # テストコードの有用性の検査
    │   ├── failure-pattern-checker.md # 起こりうるエラー・失敗のパターンの検証
    │   ├── security-checker.md    # 起こりうるセキュリティの問題の検証
    │   ├── backend-reviewer.md    # backend の専門家レビュー（初期状態は OFF）
    │   ├── frontend-reviewer.md   # frontend の専門家レビュー（初期状態は OFF）
    │   └── terraform-infra-reviewer.md # Terraform インフラの専門家レビュー（初期状態は OFF）
    └── skills/
        ├── backend-architecture/  # backend 設計指針（テンプレート。TODO を書き換える）
        ├── frontend-design/       # frontend 設計指針（テンプレート。TODO を書き換える）
        ├── infra-architecture/    # Terraform インフラ設計指針（テンプレート。TODO を書き換える）
        ├── request-interview/     # 依頼者（非エンジニア）向けの要求ヒアリング（Claude の Document か md で要求ドキュメントを作る）
        ├── spec-interview/        # 実装前の要件ヒアリング（チェックリスト方式で仕様書を作る。Claude の Document か docs/spec.md）
        └── test-guidelines/       # 言語非依存のテスト記述ガイドライン
```

## プロジェクトへの導入

`template/` は手動でコピーして使うための置き場です（Claude Code 公式の仕組みではありません）。

```bash
# 導入先プロジェクトのルートで実行
cp -R /path/to/my-claude-setting/template/. .
cat .gitignore.claude >> .gitignore && rm .gitignore.claude
```

コピー後に以下を書き換えます。

1. `CLAUDE.md` の TODO（要件資料の場所・テストの実行コマンド）
2. `.claude/skills/spec-interview/config.md`（Obsidian にプロフィールを蓄積する場合だけ、「使う」を ON にして Vault パスを書く。初期値は OFF）
3. `.claude/skills/request-interview/config.md` の確認先・規約の URL・Notion の記録先（空欄のままでも動く）
4. `.claude/skills/backend-architecture/SKILL.md` / `frontend-design/SKILL.md` / `infra-architecture/SKILL.md` の TODO（技術スタック・トークン名・ディレクトリ構成・層構成など）
5. 設計指針スキルを書き終えたものから、対応するレビュアーを ON にする（下の「レビュアーの ON/OFF」）
6. backend / frontend / infra のディレクトリ名が `backend/` / `frontend/` / `infra/` でない場合は、`CLAUDE.md` と各 reviewer の description を書き換える
7. 不要な役割（例: frontend の無いプロジェクトの `frontend-reviewer` と `frontend-design`）は削除する

プロジェクト固有の起動・停止（`/start` `/stop` `/setup` `/seed` など）は、必要に応じてプロジェクト側でスキルを追加してください。

### orchestrator の起動

orchestrator は任意で使います。使うときは、最初から orchestrator をメインのエージェントにしてセッションを始めます。

```bash
claude --agent orchestrator
```

- 通常の `claude` で始めたセッションでは orchestrator は動かず、`CLAUDE.md` のルールに沿って通常どおり作業します。
- orchestrator は、テストケース一覧の了承待ちなど、途中で指示者に確認しながら進める前提で作られています。そのため、他のエージェントからサブエージェントとして呼ぶことは `hooks/block-orchestrator-subagent.sh` で拒否しています。

### レビュアーの ON/OFF

`backend-reviewer` / `frontend-reviewer` / `terraform-infra-reviewer` は、それぞれの設計指針スキル（`backend-architecture` / `frontend-design` / `infra-architecture`）を基準にレビューします。スキルが TODO のままだと基準がないため、初期状態では `.claude/settings.json` の `permissions.deny` で起動できないようにしています（OFF）。

```json
"deny": [
  "Agent(backend-reviewer)",
  "Agent(frontend-reviewer)",
  "Agent(terraform-infra-reviewer)",
  ...
]
```

- ON にする: スキルを書き終えたら、対応する行を `deny` から消す
- OFF に戻す: 行を `deny` に戻す
- OFF のレビュアーは、orchestrator も通常のセッションも起動せず、飛ばしたことを作業の報告に書きます
- `failure-pattern-checker` / `security-checker` などのチェッカーは設計指針スキルに頼らないため、初期状態から ON です

### 補足: 公式の配布手段

複数プロジェクトで同じ設定を使い回す仕組みとして、Claude Code には次のものがあります。

- **ユーザー設定（`~/.claude/agents/`, `~/.claude/skills/`）**: 置くと全プロジェクトで使えます。ただし全プロジェクトに効いてしまうため、orchestrator 体制のようにプロジェクトごとに使うか選びたい設定には向きません。
- **プラグイン**: agents / skills / hooks をまとめて配布し、`/plugin` コマンドでプロジェクトごとにインストール・更新できます。更新を各プロジェクトに反映しやすくなります。ただしプロジェクト固有の内容（CLAUDE.md、設計指針の中身）はプロジェクト側に書く必要があります。

### Claude Desktop / claude.ai へのインポート

`template/.claude/skills/` 配下の各スキルを、Claude Desktop や claude.ai の「スキルをアップロード」から取り込める `.skill` ファイル（スキル名のフォルダを格納した zip）に変換したものを `dist/skills/` に置いています。スキルを編集したら次のコマンドで作り直してください。

```bash
python3 scripts/package_skills.py
```

- 元のスキルファイルは変更しません。
- `disable-model-invocation` など Claude Code 固有の frontmatter キーは、パッケージ内の SKILL.md からのみ取り除きます（アップロード時のエラーを避けるため）。

## 要求ヒアリングから仕様設計への引き継ぎ

エンジニアに開発を依頼する側の人（ユーザーサポート・PO・デザイナーなど）は、`request-interview` スキルで要望をまとめます。仕様には踏み込まず、依頼者にしか答えられないこと（困りごと・現場の事実・成功の状態・優先度・期限）と、確認漏れ（利用規約・個人情報・告知など）だけを聞きます。

- 出力：出力前に依頼者に「Claude の Document に書く（推奨）」か「md ファイルに出力する」かを選んでもらいます。Document は 1依頼 = 1タブで、要求用の Document の URL がリポジトリの開発ルールをまとめた資料等に記録されていればその Document の tabs に新しいタブを足し、なければ（リポジトリに対する要求でないときも）新しく作ります。作成後、依頼者に Share からの共有を案内します。Notion には Document の Export からコピーできます
- リポジトリに対する要求で Document・画面デザインを新しく作ったときは、リポジトリには書き込まず、「今後も要求定義の結果をこの Document に追記していく場合は、本リポジトリに記録先として記載してください（担当者がいるのであれば、その方に依頼してください）。」と依頼者に伝えます
- ヒアリングがひと通り終わったら、依頼者に確認したうえで Claude の Design アーティファクトに画面デザインを作ります。リポジトリに対する要求では、既存の実装から対象の画面を再現し、その横に追加実装案を並べます。デザイン用の Artifact の URL が `docs/design.md` その他開発ルールをまとめた資料等に記録されていればその Design のキャンバスの pages に新しいページを足し、なければ新しく作ります。作ったデザインの URL は要求ドキュメントの「画面デザイン」に載ります
- 仕様書の記録先：リポジトリで初めての仕様ヒアリングで、仕様書用の Document も `docs/spec.md` も見つからないときは、Claude の Document（推奨）か md かを聞きます。Document を選ぶと「今後も追記する資料として README に記載しますか？」と聞き、記載するなら README に記録のルールと URL を書きます。次回以降はその Document に新しいタブを作って記録します（`spec-interview/references/spec-storage.md`）。要求ドキュメントとは別の Document を使います
- エンジニアは要求ドキュメント（「状態」が合意済みの Document の URL、または依頼者から受け取った md ファイル）を spec-interview に渡すと、Phase 1 が要約の確認だけになり、骨組みの初期値に要求ドキュメントの内容が使われます（`spec-interview/references/request-handoff.md`）
- 仕様レビュー（Phase 7）：レビュアーの指示は spec-interview の中（`spec-interview/references/spec-review.md`）にあり、読むことしかできないサブエージェントに渡して起動します。エージェントの定義を別に入れなくても、スキルだけで動きます

## エージェントの動きの流れ

`claude --agent orchestrator` で始めたセッションでの流れです。orchestrator は仕様書・テスト・実装・PROGRESS.md の編集を自身で行い、チェックとレビューを専門のサブエージェントに任せます。

チェッカー・レビュアーには、実装者の説明に引きずられずに確認してもらうため、実装の説明や意図は渡さず、各エージェントの「受け取る情報」の表に書かれた情報（差分の範囲・仕様書のパス・PROGRESS.md の該当する節、test-checker には了承済みのテストケース一覧など）だけを渡します。

### orchestrator 以外からの利用

チェッカー・レビュアーは orchestrator 以外（通常のセッション）からも使えます。

- 各エージェントの冒頭に「受け取る情報」の表（情報・必須か任意か・ない場合の扱い）があり、何を渡せばよいかの正本はここです。呼び出す側は、起動する前にこの表を読みます（`CLAUDE.md` の「チェッカー・レビュアーへの依頼と結果の扱い」）
- テストケース一覧や PROGRESS.md など任意の情報がない場合は、表の「ない場合の扱い」に従って確認できる範囲だけを確認し、確認しなかったことを結果に書きます
- 結果の書き方は、各エージェントの「出力」の節にあります

図の中の印の意味は次のとおりです。

- `⏸ 停止` … **必ず**作業を止め、指示者の了承・判断を待つ
- `⚠ 停止` … 該当する状況が起きた場合**のみ**作業を止め、指示者に確認する

```
指示者（ユーザー）
   │ 作業依頼
   ▼
orchestrator ── PROGRESS.md を読み、状態と残作業を確認
   │
   │ ⓪ 仕様ヒアリング（要件が曖昧な依頼・機能追加の相談のとき）
   ├─  orchestrator        : spec-interview スキルで指示者にヒアリング・提案し、合意した項目を仕様書（Document または docs/spec.md）に反映
   ├─▶ 仕様レビュー        : spec-interview の手順でサブエージェントが仕様書を第三者視点でレビュー
   │     ⏸ 停止 ─ 各フェーズの終わりと仕様確定時に指示者の合意を待つ
   │
   │ ① 仕様の確定
   ├─  orchestrator        : 仕様書（docs）に今回の仕様を反映
   │
   │ ② テスト先行
━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⏸ 停止  仕様書の変更点 + テストケース一覧を提示し、了承を待つ
         （指摘があれば直して再提示 → 了承されるまで先へ進まない）
━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ├─  orchestrator        : テストだけを書く（本体コードは触らない）
   │     ⚠ 停止 ─ 了承済みの一覧から外れるテストの追加・削除、既存テストの変更が必要になった
   ├─  orchestrator        : 全テストを実行し、狙いどおり失敗することを確認
   │     ⚠ 停止 ─ 狙い以外のテストが失敗した
   ├─▶ test-checker        : テスト内容を確認（実装前は 1 回まで）
   │
   │ ③ 実装（Step ごとに繰り返す）
   ├─  orchestrator        : 実装（設計指針スキルを参照）
   ├─  orchestrator        : 全テストを実行し、全件成功を確認
   │     ⚠ 停止 ─ 狙い以外の失敗がある / テストと仕様・要件の食い違いに気づいた
   │
   │ ④ 実装後のチェック（3 つを並列）
   ├─▶ test-checker        : 了承済みのテストケース一覧どおりにテストが書かれているかを確認
   ├─▶ overview-checker    : 他機能・サービス全体への影響、既存の仕組みとの重複を確認
   │     ⚠ 停止 ─ 仕様が大きく変わる修正や、指示者の指示に反する修正が必要になった
   ├─▶ requirement-checker : 仕様書・PROGRESS.md の決定事項から要求の一覧を作り、満たしているか照合
   │
   │ ⑤ レビュー（変更した範囲のレビュアーと 2 つのチェッカーを並列。OFF のレビュアーは飛ばす）
   ├─▶ backend-reviewer         : backend-architecture スキルに沿ってレビュー
   ├─▶ frontend-reviewer        : frontend-design スキルに沿ってレビュー
   ├─▶ terraform-infra-reviewer : infra-architecture スキルに沿ってレビュー
   ├─▶ failure-pattern-checker  : 起こりうるエラー・失敗のパターンを検証
   ├─▶ security-checker         : 起こりうるセキュリティの問題を検証
   │     ⚠ 停止 ─ ④⑤ のチェッカー・レビュアーが「ユーザーに確認したい点」を出した
   │     ⚠ 停止 ─ インフラの指摘を直す前（費用への影響を示し、直すものを選んでもらう）
   │
   │ ⑥ 進捗の記録
   ├─  orchestrator        : PROGRESS.md を更新
   │
━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⏸ 停止  指示者へ完了報告
         （次の Step に進むか・コミットするかなどは指示者の判断を待つ）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 指示者に判断が委ねられる場面

| 区分 | タイミング | 指示者に求められること |
| --- | --- | --- |
| ⏸ 必ず | ⓪ 仕様ヒアリング（行う場合） | 各フェーズの終わりに合意し、最後に `docs/spec.md` 全体を確定する |
| ⏸ 必ず | ② テストを書く前 | 仕様書の変更点とテストケース一覧が要求を満たしているかを確認し、了承する |
| ⏸ 必ず | 作業の最後 | 完了報告を確認し、次の Step に進むか・コミットするかなどを判断する |
| ⚠ 条件付き | ② テスト作成中 | 了承済みの一覧から外れるテストの追加・削除や、既存テストの変更を認めるか判断する |
| ⚠ 条件付き | ②③ テスト実行時 | 狙い以外のテストの失敗や、テストと仕様・要件の食い違いへの対応を決める |
| ⚠ 条件付き | ④ overview-checker | 仕様が大きく変わる修正や、指示に反する修正を行うか判断する |
| ⚠ 条件付き | ④⑤ チェック・レビュー | チェッカー・レビュアーからの「ユーザーに確認したい点」に回答する |
| ⚠ 条件付き | ⑤ インフラの指摘 | 指摘ごとの「問題・修正前・修正後・費用への影響」を見て、直すものを選ぶ |
| ⚠ 条件付き | 作業の報告 | レビュアーからの「規約への追記の提案」を、設計指針スキルに反映するか判断する |

これ以外の場面でも、orchestrator はチェックの結果と修正方針を都度表示します。止まらずに進みますが、内容が違っていれば途中で指示を出して軌道修正できます。

### 流れの中のルール

- **確認事項は指示者へ**: チェッカー・レビュアーが「ユーザーに確認したい点」を出した場合、orchestrator は自分で判断せず指示者に質問してから進めます。
- **チェック結果は都度表示**: チェックの結果と修正方針を表示し、指示者が途中で軌道修正できるようにします。
- **ループの上限**: チェック → 修正 のループは 1 セッション最大 3 回（実装前のテスト確認は 1 回）。
- **範囲を広げない**: Step で決めた範囲を超える修正は、致命的なもの以外は今後のタスク候補としてメモに留めます。
- **レビュアーはコミットしない**: reviewer / checker は読み取りと指摘のみで、コード修正・コミットは行いません。
- **知見の蓄積**: backend-reviewer / frontend-reviewer / terraform-infra-reviewer は `memory: project` により、レビューで得た知見をリポジトリ直下の `.claude/agent-memory/` に蓄積し、次回以降のレビューに活かします。機能をまたいで通用する規約は「規約への追記の提案」として出し、指示者の了承を得て設計指針スキルに反映します。
- **apply はしない**: インフラの `terraform apply` / `destroy` は指示者が行います。エージェントは実行しません。
