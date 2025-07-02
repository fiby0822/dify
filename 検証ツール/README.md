# Dify YAML検証ツール

## 概要

Dify YAMLファイルの自動検証ツールです。インポート前にYAMLファイルの構造と内容を検証し、エラーやクラッシュの原因となる問題を事前に検出します。

## 機能

### エラーチェック（修正必須）
- YAMLシンタックス検証
- 必須フィールド存在確認
- 禁止フィールド不在確認
- ノードID重複チェック
- エッジ整合性チェック
- if-else条件ID確認
- 変数参照パス検証
- YAMLコメントチェック
- CODEノードoutputsチェック

### 警告チェック（推奨事項）
- Unicode比較演算子の検出（ASCII変換推奨）
- ノード数上限チェック（30個超）
- Answerノード数チェック（5個超）
- YAMLファイル行数チェック（800行超）
- CODEノード行数チェック（100行超）
- 変数型の確認（text → text-input）
- boolean値の型確認

## 必要要件

- Python 3.6以上
- PyYAMLライブラリ

## インストール

```bash
# PyYAMLのインストール
pip install pyyaml

# 実行権限の付与（初回のみ）
chmod +x validate_dify.py
```

## 使用方法

### 基本的な使用
```bash
python validate_dify.py [YAMLファイルパス]

# または直接実行
./validate_dify.py [YAMLファイルパス]
```

### オプション
```bash
# 詳細情報を表示
python validate_dify.py -v [YAMLファイルパス]

# 警告を非表示
python validate_dify.py --no-warnings [YAMLファイルパス]

# ヘルプを表示
python validate_dify.py -h
```

## 出力形式

### エラー（修正必須）
```
❌ app.use_icon_as_answer_iconが見つかりません
❌ YAMLコメントが含まれています。削除してください
```

### 警告（推奨事項）
```
⚠️  Unicode比較演算子が使用されています。ASCII文字（>=, <=, !=）の使用を推奨します
⚠️  総ノード数が30個を超えています（現在: 35個）
```

### 成功
```
✅ 検証に合格しました
```

## 終了コード

- `0`: エラーなし（警告のみ、または問題なし）
- `1`: エラーあり

## 検証項目詳細

### 1. YAMLシンタックス検証
- YAMLとして正しい構文であること
- インデントが一貫していること（スペース2個推奨）
- 文字エンコーディングがUTF-8であること

### 2. 必須フィールド存在確認
- `app`セクション
  - `app.use_icon_as_answer_icon`
  - `app.name`
  - `app.description`
  - `app.icon`
  - `app.icon_background`
  - `app.mode`
- `dependencies`（空配列でも必須）
- `kind: app`
- `version: 0.3.0`
- `workflow`セクション
  - `workflow.conversation_variables`
  - `workflow.environment_variables`
  - `workflow.features`（advanced-chatモードの場合）
  - `workflow.graph`
    - `workflow.graph.nodes`
    - `workflow.graph.edges`

### 3. 禁止フィールド不在確認
以下のフィールドがトップレベルに存在しないことを確認：
- `fiby_version`
- `main`
- `metadata`
- `description`
- `hash`
- `mode`
- `system_prompt`
- `graph`
- `variables`

### 4. ノードID重複チェック
- すべてのノードIDがユニークであること
- IDがsnake_case形式であること（推奨）

### 5. エッジ整合性チェック
- すべてのエッジのsource/targetが実在するノードIDであること
- エッジに必須フィールドが含まれていること
  - `data.isInLoop`（isInIterationではない）
  - `selected`
  - `zIndex`
- IF-ELSEノードのsourceHandleがcase_idまたは"false"であること

### 6. if-else条件ID確認
- すべてのif-elseノードで、各条件に一意のIDが設定されていること
- case_idがidと一致していること

### 7. 変数参照パス検証
- プロンプト内の変数参照（{{#node_id.variable#}}）が実在するノードを指していること

### 8. YAMLコメントチェック
- YAMLファイル内に#で始まるコメントが含まれていないこと

### 9. 比較演算子チェック
- Unicode文字（≥、≤、≠）の使用を検出し、ASCII文字（>=、<=、!=）への変換を提案

### 10. CODEノードoutputsチェック
- outputsにdescriptionフィールドが含まれていないこと
- 正しい形式（value_selectorとvariableの配列）であること

## 使用例

```bash
# ファイルの検証
$ python validate_dify.py sample.yaml

=== Dify YAML検証: sample.yaml ===

=== エラー（修正必須） ===
❌ app.use_icon_as_answer_iconが見つかりません
❌ YAMLコメントが含まれています。削除してください

=== 警告（推奨事項） ===
⚠️  Unicode比較演算子 '≥' が2箇所で使用されています。ASCII文字 '>=' の使用を推奨します
⚠️  総ノード数が30個を超えています（現在: 35個）

❌ 2件のエラー、2件の警告

# 詳細情報付きで実行
$ python validate_dify.py -v sample.yaml

=== Dify YAML検証: sample.yaml ===

✅ 検証に合格しました

=== 詳細情報 ===
ファイルサイズ: 15234 bytes
行数: 521 行
ノード数: 12
エッジ数: 15
```

## トラブルシューティング

### PyYAMLがインストールされていない場合
```bash
pip install pyyaml
# または
pip3 install pyyaml
```

### 実行権限エラーの場合
```bash
chmod +x validate_dify.py
```

### Python3が見つからない場合
```bash
# Pythonのパスを確認
which python3

# パスが異なる場合は、スクリプトの1行目を修正
#!/usr/bin/env python3
```

## 更新履歴

- 2025-07-01: 初版作成