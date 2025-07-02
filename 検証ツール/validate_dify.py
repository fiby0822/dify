#!/usr/bin/env python3
"""
Dify YAML検証ツール
Difyアプリケーション定義YAMLファイルの包括的な検証を行います。
"""

import yaml
import sys
import re
import json
from typing import Dict, List, Tuple, Any, Set
from pathlib import Path
import argparse


class DifyYAMLValidator:
    """Dify YAMLファイルの検証クラス"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.content: str = ""
        self.data: Dict[str, Any] = {}
        
    def validate(self) -> Tuple[List[str], List[str]]:
        """メイン検証メソッド"""
        # 1. YAMLシンタックス検証
        if not self._validate_yaml_syntax():
            return self.errors, self.warnings
            
        # 2. 必須フィールド存在確認
        self._check_required_fields()
        
        # 3. 禁止フィールド不在確認
        self._check_forbidden_fields()
        
        # 4. ノードID重複チェック
        self._check_node_id_duplicates()
        
        # 5. エッジ整合性チェック
        self._check_edge_consistency()
        
        # 6. if-else条件ID確認
        self._check_if_else_conditions()
        
        # 7. 変数参照パス検証
        self._check_variable_references()
        
        # 8. YAMLコメントチェック
        self._check_yaml_comments()
        
        # 9. 比較演算子チェック
        self._check_comparison_operators()
        
        # 10. CODEノードoutputsチェック
        self._check_code_node_outputs()
        
        # 警告レベルチェック
        self._check_warnings()
        
        return self.errors, self.warnings
    
    def _validate_yaml_syntax(self) -> bool:
        """YAMLシンタックス検証"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                
            # UTF-8エンコーディングチェック
            try:
                self.content.encode('utf-8')
            except UnicodeDecodeError:
                self.errors.append("ファイルがUTF-8でエンコードされていません")
                return False
                
            # YAML構文チェック
            self.data = yaml.safe_load(self.content)
            
            # インデントチェック（スペース2個）
            lines = self.content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#'):
                    # 先頭のスペース数をチェック
                    indent = len(line) - len(line.lstrip())
                    if indent % 2 != 0:
                        self.warnings.append(f"行{i+1}: インデントが2の倍数ではありません（{indent}スペース）")
                        
            return True
            
        except yaml.YAMLError as e:
            self.errors.append(f"YAMLパースエラー: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"ファイルが見つかりません: {self.file_path}")
            return False
        except Exception as e:
            self.errors.append(f"ファイル読み込みエラー: {e}")
            return False
    
    def _check_required_fields(self):
        """必須フィールド存在確認"""
        # トップレベル必須フィールド
        if 'app' not in self.data:
            self.errors.append("app:セクションが見つかりません")
        else:
            app = self.data['app']
            required_app_fields = [
                'use_icon_as_answer_icon', 'name', 'description', 
                'icon', 'icon_background', 'mode'
            ]
            for field in required_app_fields:
                if field not in app:
                    self.errors.append(f"app.{field}が見つかりません")
        
        if 'dependencies' not in self.data:
            self.errors.append("dependencies:が見つかりません")
            
        if 'kind' not in self.data or self.data['kind'] != 'app':
            self.errors.append("kind: appが見つかりません")
            
        if 'version' not in self.data or self.data['version'] != '0.3.0':
            self.errors.append("version: 0.3.0が見つかりません")
            
        # workflowセクション
        if 'workflow' not in self.data:
            self.errors.append("workflow:セクションが見つかりません")
        else:
            workflow = self.data['workflow']
            
            if 'conversation_variables' not in workflow:
                self.errors.append("workflow.conversation_variablesが見つかりません")
                
            if 'environment_variables' not in workflow:
                self.errors.append("workflow.environment_variablesが見つかりません")
                
            # advanced-chatモードの場合のみfeaturesが必須
            if self.data.get('app', {}).get('mode') == 'advanced-chat':
                if 'features' not in workflow:
                    self.errors.append("workflow.features (advanced-chatモードで必須)が見つかりません")
                    
            if 'graph' not in workflow:
                self.errors.append("workflow.graphが見つかりません")
            else:
                graph = workflow['graph']
                if 'nodes' not in graph:
                    self.errors.append("workflow.graph.nodesが見つかりません")
                if 'edges' not in graph:
                    self.errors.append("workflow.graph.edgesが見つかりません")
    
    def _check_forbidden_fields(self):
        """禁止フィールド不在確認"""
        forbidden_fields = [
            'fiby_version', 'main', 'metadata', 'description',
            'hash', 'mode', 'system_prompt', 'graph', 'variables'
        ]
        
        for field in forbidden_fields:
            if field in self.data:
                self.errors.append(f"禁止フィールド'{field}'がトップレベルに存在します")
                
        # hashフィールドの特別チェック（手動追加の場合）
        if 'hash' in self.content:
            self.warnings.append("hashフィールドが含まれています。手動で追加しないでください")
    
    def _check_node_id_duplicates(self):
        """ノードID重複チェック"""
        workflow = self.data.get('workflow', {})
        graph = workflow.get('graph', {})
        nodes = graph.get('nodes', [])
        
        node_ids: Set[str] = set()
        for node in nodes:
            if 'id' in node:
                node_id = node['id']
                if node_id in node_ids:
                    self.errors.append(f"重複したノードID: {node_id}")
                node_ids.add(node_id)
                
                # snake_case形式チェック（推奨）
                if not re.match(r'^[a-z][a-z0-9_]*$', node_id):
                    self.warnings.append(f"ノードID '{node_id}' はsnake_case形式ではありません（推奨）")
    
    def _check_edge_consistency(self):
        """エッジ整合性チェック"""
        workflow = self.data.get('workflow', {})
        graph = workflow.get('graph', {})
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        
        # ノードIDのセットを作成
        node_ids = {node.get('id') for node in nodes if 'id' in node}
        
        for i, edge in enumerate(edges):
            edge_id = f"edges[{i}]"
            
            # source/targetの存在確認
            source = edge.get('source')
            target = edge.get('target')
            
            if not source:
                self.errors.append(f"{edge_id}: sourceが指定されていません")
            elif source not in node_ids:
                self.errors.append(f"{edge_id}: source '{source}' は存在しないノードIDです")
                
            if not target:
                self.errors.append(f"{edge_id}: targetが指定されていません")
            elif target not in node_ids:
                self.errors.append(f"{edge_id}: target '{target}' は存在しないノードIDです")
            
            # 必須フィールドチェック
            data = edge.get('data', {})
            if 'isInLoop' not in data:
                self.errors.append(f"{edge_id}: data.isInLoopが見つかりません")
            if 'isInIteration' in data:
                self.warnings.append(f"{edge_id}: data.isInIterationは使用しないでください。data.isInLoopを使用してください")
                
            if 'selected' not in edge:
                self.errors.append(f"{edge_id}: selectedが見つかりません")
                
            if 'zIndex' not in edge:
                self.errors.append(f"{edge_id}: zIndexが見つかりません")
            
            # IF-ELSEノードのsourceHandleチェック
            source_handle = edge.get('sourceHandle')
            if source_handle:
                # ソースノードを見つける
                source_node = next((n for n in nodes if n.get('id') == source), None)
                if source_node and source_node.get('data', {}).get('type') == 'if-else':
                    if source_handle != 'false' and not source_handle.startswith('case_id_'):
                        self.errors.append(f"{edge_id}: IF-ELSEノードのsourceHandleは'false'またはcase_idである必要があります")
    
    def _check_if_else_conditions(self):
        """if-else条件ID確認"""
        workflow = self.data.get('workflow', {})
        graph = workflow.get('graph', {})
        nodes = graph.get('nodes', [])
        
        for node in nodes:
            if node.get('data', {}).get('type') == 'if-else':
                node_id = node.get('id', 'unknown')
                conditions = node.get('data', {}).get('conditions', [])
                
                condition_ids: Set[str] = set()
                for i, condition in enumerate(conditions):
                    cond_id = condition.get('id')
                    case_id = condition.get('case_id')
                    
                    if not cond_id:
                        self.errors.append(f"ノード{node_id}: 条件{i+1}にIDが設定されていません")
                    else:
                        if cond_id in condition_ids:
                            self.errors.append(f"ノード{node_id}: 重複した条件ID: {cond_id}")
                        condition_ids.add(cond_id)
                        
                    if case_id != cond_id:
                        self.errors.append(f"ノード{node_id}: case_id({case_id})がid({cond_id})と一致しません")
    
    def _check_variable_references(self):
        """変数参照パス検証"""
        workflow = self.data.get('workflow', {})
        graph = workflow.get('graph', {})
        nodes = graph.get('nodes', [])
        
        # 変数参照パターン
        var_pattern = re.compile(r'\{\{#([^.]+)\.([^#]+)#\}\}')
        
        # ノードIDのセット
        node_ids = {node.get('id') for node in nodes if 'id' in node}
        
        # ノードの実行順序を推定（簡易版）
        # TODO: より正確な実行順序の解析が必要
        
        for node in nodes:
            node_id = node.get('id', 'unknown')
            node_data = node.get('data', {})
            
            # プロンプトや他のテキストフィールドを検査
            text_fields = []
            if 'prompt' in node_data:
                text_fields.append(('prompt', node_data['prompt']))
            if 'text' in node_data:
                text_fields.append(('text', node_data['text']))
            if 'query' in node_data:
                text_fields.append(('query', node_data['query']))
                
            for field_name, text in text_fields:
                if isinstance(text, str):
                    matches = var_pattern.findall(text)
                    for ref_node_id, var_name in matches:
                        if ref_node_id not in node_ids:
                            self.errors.append(
                                f"ノード{node_id}.{field_name}: 存在しないノード'{ref_node_id}'への参照"
                            )
    
    def _check_yaml_comments(self):
        """YAMLコメントチェック"""
        lines = self.content.split('\n')
        
        for i, line in enumerate(lines):
            # コメント行のパターン
            # 行頭の#、または文字列外の#
            if re.match(r'^\s*#', line):
                self.errors.append(f"行{i+1}: YAMLコメントが含まれています")
            elif '#' in line:
                # 文字列内でない#をチェック（簡易版）
                # より正確には、YAMLパーサーの状態を追跡する必要がある
                if not ('"' in line[:line.index('#')] or "'" in line[:line.index('#')]):
                    self.errors.append(f"行{i+1}: YAMLコメントが含まれている可能性があります")
    
    def _check_comparison_operators(self):
        """比較演算子チェック"""
        unicode_ops = {
            '≥': '>=',
            '≤': '<=',
            '≠': '!='
        }
        
        for unicode_op, ascii_op in unicode_ops.items():
            if unicode_op in self.content:
                count = self.content.count(unicode_op)
                self.warnings.append(
                    f"Unicode比較演算子 '{unicode_op}' が{count}箇所で使用されています。"
                    f"ASCII文字 '{ascii_op}' の使用を推奨します"
                )
    
    def _check_code_node_outputs(self):
        """CODEノードoutputsチェック"""
        workflow = self.data.get('workflow', {})
        graph = workflow.get('graph', {})
        nodes = graph.get('nodes', [])
        
        for node in nodes:
            if node.get('data', {}).get('type') == 'code':
                node_id = node.get('id', 'unknown')
                outputs = node.get('data', {}).get('outputs', {})
                
                if isinstance(outputs, dict):
                    for key, output in outputs.items():
                        if isinstance(output, dict):
                            if 'description' in output:
                                self.errors.append(
                                    f"CODEノード{node_id}: outputs.{key}にdescriptionフィールドが含まれています"
                                )
                            # 正しい形式のチェック
                            if 'value_selector' not in output or 'variable' not in output:
                                self.errors.append(
                                    f"CODEノード{node_id}: outputs.{key}にvalue_selectorまたはvariableが見つかりません"
                                )
    
    def _check_warnings(self):
        """警告レベルチェック"""
        workflow = self.data.get('workflow', {})
        graph = workflow.get('graph', {})
        nodes = graph.get('nodes', [])
        
        # ノード数チェック
        total_nodes = len(nodes)
        if total_nodes > 30:
            self.warnings.append(f"総ノード数が30個を超えています（現在: {total_nodes}個）")
            
        # Answerノード数チェック
        answer_nodes = sum(1 for n in nodes if n.get('data', {}).get('type') == 'answer')
        if answer_nodes > 5:
            self.warnings.append(f"Answerノードが5個を超えています（現在: {answer_nodes}個）")
        
        # IF-ELSE深さチェック（簡易版）
        # TODO: より正確な深さ計算の実装
        
        # ファイル行数チェック
        line_count = len(self.content.split('\n'))
        if line_count > 800:
            self.warnings.append(f"YAMLファイルが800行を超えています（現在: {line_count}行）")
        
        # CODEノードの行数チェック
        for node in nodes:
            if node.get('data', {}).get('type') == 'code':
                node_id = node.get('id', 'unknown')
                code = node.get('data', {}).get('code', '')
                if isinstance(code, str):
                    code_lines = len(code.split('\n'))
                    if code_lines > 100:
                        self.warnings.append(
                            f"CODEノード{node_id}が100行を超えています（現在: {code_lines}行）"
                        )
        
        # 変数型チェック
        start_nodes = [n for n in nodes if n.get('data', {}).get('type') == 'start']
        for node in start_nodes:
            variables = node.get('data', {}).get('variables', [])
            for var in variables:
                if var.get('type') == 'text':
                    var_name = var.get('variable', 'unknown')
                    self.warnings.append(
                        f"startノードの変数'{var_name}': type='text'ではなく'text-input'を使用してください"
                    )
        
        # boolean値の型チェック
        self._check_boolean_types(self.data)
    
    def _check_boolean_types(self, obj: Any, path: str = ""):
        """boolean値の型確認（再帰的）"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if isinstance(value, str) and value.lower() in ['true', 'false']:
                    self.warnings.append(
                        f"{new_path}: 文字列'{value}'が使用されています。"
                        f"boolean型の{value.lower()}を使用することを検討してください"
                    )
                self._check_boolean_types(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._check_boolean_types(item, f"{path}[{i}]")


def main():
    """メインエントリポイント"""
    parser = argparse.ArgumentParser(
        description='Dify YAMLファイルの検証ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
出力形式:
  ❌ エラー（修正必須）
  ⚠️  警告（推奨事項）
  ✅ 検証に合格

終了コード:
  0: エラーなし（警告のみ、または問題なし）
  1: エラーあり
        """
    )
    parser.add_argument('yaml_file', help='検証するYAMLファイルのパス')
    parser.add_argument('-v', '--verbose', action='store_true', help='詳細な出力')
    parser.add_argument('--no-warnings', action='store_true', help='警告を表示しない')
    
    args = parser.parse_args()
    
    # 検証実行
    validator = DifyYAMLValidator(args.yaml_file)
    errors, warnings = validator.validate()
    
    # 結果出力
    print(f"=== Dify YAML検証: {args.yaml_file} ===\n")
    
    if errors:
        print("=== エラー（修正必須） ===")
        for error in errors:
            print(f"❌ {error}")
        print()
    
    if warnings and not args.no_warnings:
        print("=== 警告（推奨事項） ===")
        for warning in warnings:
            print(f"⚠️  {warning}")
        print()
    
    if not errors and not warnings:
        print("✅ 検証に合格しました")
    elif not errors and warnings:
        print(f"✅ エラーなし（{len(warnings)}件の警告あり）")
    else:
        print(f"❌ {len(errors)}件のエラー、{len(warnings)}件の警告")
    
    # 詳細情報
    if args.verbose:
        print(f"\n=== 詳細情報 ===")
        print(f"ファイルサイズ: {Path(args.yaml_file).stat().st_size} bytes")
        print(f"行数: {len(validator.content.split(chr(10)))} 行")
        if validator.data:
            workflow = validator.data.get('workflow', {})
            graph = workflow.get('graph', {})
            print(f"ノード数: {len(graph.get('nodes', []))}")
            print(f"エッジ数: {len(graph.get('edges', []))}")
    
    # 終了コード
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()