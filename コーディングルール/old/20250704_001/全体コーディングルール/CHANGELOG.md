# Dify開発用 全体コーディングルール 改訂履歴

## 概要
このファイルは、Dify開発用全体コーディングルールの改訂履歴を記録したものです。

## 変更履歴

### 2025.07.03
- **ファイル分割によるリファクタリング実施**
  - 全体コーディングルール.md（33,000トークン超）を8つのファイルに分割
  - 00_index.md：インデックスファイルを新規作成
  - 01～08の機能別ファイルに分割・整理
  - 相互参照リンクを追加して使いやすさを向上
  - 基本方針セクションを00_index.mdに追加

### 2025.07.03以前の主要な変更
- **コーディングルール大幅更新：エラー分析に基づく変数参照記法の統一と品質向上**
- **template-transform許可とエッジ設定整合性対応**
- **Google Sheets操作関連の包括的な更新**
- **エラー分析に基づく包括的アップデート**

### 2025.01.01～2025.07.02の改訂項目
以下の項目について継続的な改善を実施：
- よくある失敗パターンの追加・更新
- YAMLファイル基本構造の明確化
- 命名規則の統一
- ワークフロー設計原則の確立
- ナレッジベース管理方法の標準化
- 変数管理ルールの整備
- 品質管理基準の強化
- セキュリティ考慮事項の追加
- パフォーマンス最適化ガイドラインの策定
- ドキュメント化基準の制定
- 互換性とアップデート方針の明確化
- トラブルシューティング指針の拡充
- 型定義リファレンスの完成
- 最小構成テンプレートの提供
- 開発時の推奨フローの確立
- システム変数リファレンスの整備
- モード別ベストプラクティスの文書化
- コード実行ノードの注意事項追加
- パフォーマンスと拡張性ガイドラインの策定
- 最終チェックリストの作成
- よくある質問（FAQ）の整備
- デバッグ設定管理方法の標準化
- hashフィールドの取り扱い方針の明確化
- マーケットプレイス依存関係管理の確立
- トークン数管理とモデル選択ガイドの作成
- 外部ツール（Tool）ノードの使用方法の文書化

## 今後の改訂予定
- 各ファイルのさらなる最適化
- 実例コードの追加
- エラーパターンの継続的な収集と文書化
- パフォーマンスベストプラクティスの拡充

## 貢献者
このドキュメントの改善に貢献いただいたすべての開発者に感謝いたします。

---
*最終更新日：2025年7月3日*