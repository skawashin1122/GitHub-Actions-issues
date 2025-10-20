import os
import requests
import time
from typing import List, Dict

class GitHubIssuesCopier:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
    
    def get_issues(self, owner: str, repo: str, state: str = 'all') -> List[Dict]:
        """指定されたリポジトリからissuesを取得"""
        issues = []
        page = 1
        
        while True:
            url = f'{self.base_url}/repos/{owner}/{repo}/issues'
            params = {
                'state': state,
                'page': page,
                'per_page': 100,
                'filter': 'all'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            page_issues = response.json()
            
            # Pull Requestsを除外
            page_issues = [issue for issue in page_issues if 'pull_request' not in issue]
            
            if not page_issues:
                break
                
            issues.extend(page_issues)
            page += 1
            
            print(f'取得済み: {len(issues)} issues')
            time.sleep(1)  # レート制限対策
        
        return issues
    
    def get_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict]:
        """特定のissueのコメントを取得"""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_issue(self, owner: str, repo: str, title: str, body: str, 
                    labels: List[str] = None, state: str = 'open') -> Dict:
        """新しいissueを作成"""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues'
        data = {
            'title': title,
            'body': body
        }
        
        if labels:
            data['labels'] = labels
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise Exception(f"リポジトリ {owner}/{repo} が見つからないか、アクセス権がありません。リポジトリが存在するか、トークンにrepo権限があるかを確認してください。")
            else:
                raise e
        
        created_issue = response.json()
        
        # 元のissueがcloseされていた場合、新しいissueもclose
        if state == 'closed':
            self.close_issue(owner, repo, created_issue['number'])
        
        return created_issue
    
    def create_comment(self, owner: str, repo: str, issue_number: int, body: str):
        """issueにコメントを追加"""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments'
        data = {'body': body}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def close_issue(self, owner: str, repo: str, issue_number: int):
        """issueをクローズ"""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}'
        data = {'state': 'closed'}
        response = requests.patch(url, headers=self.headers, json=data)
        response.raise_for_status()
    
    def copy_issues(self, source_owner: str, source_repo: str, 
                   dest_owner: str, dest_repo: str, 
                   include_comments: bool = True,
                   copy_state: bool = True):
        """issuesをコピー"""
        print(f'コピー元: {source_owner}/{source_repo}')
        print(f'コピー先: {dest_owner}/{dest_repo}')
        print('=' * 50)
        
        # 元のissuesを取得
        source_issues = self.get_issues(source_owner, source_repo)
        print(f'\n合計 {len(source_issues)} 件のissuesを取得しました\n')
        
        for i, issue in enumerate(source_issues, 1):
            print(f'[{i}/{len(source_issues)}] コピー中: #{issue["number"]} - {issue["title"]}')
            
            # issueの本文を構築（元のissue情報を含める）
            original_link = issue['html_url']
            original_author = issue['user']['login']
            created_at = issue['created_at']
            
            # body = f'> **元のissue**: {original_link}\n'
            # body += f'> **作成者**: @{original_author}\n'
            # body += f'> **作成日**: {created_at}\n\n'
            # body += '---\n\n'
            body = issue['body'] or ''
            
            # ラベルを取得（コピー先に存在しない場合は無視される）
            labels = [label['name'] for label in issue['labels']]
            
            # issueの状態
            state = issue['state'] if copy_state else 'open'
            
            try:
                # 新しいissueを作成
                new_issue = self.create_issue(
                    dest_owner, dest_repo, 
                    issue['title'], body, 
                    labels, state
                )
                
                # コメントをコピー
                if include_comments:
                    comments = self.get_comments(source_owner, source_repo, issue['number'])
                    if comments:
                        print(f'  → {len(comments)} 件のコメントをコピー中...')
                        for comment in comments:
                            comment_body = f'**@{comment["user"]["login"]}** ({comment["created_at"]}):\n\n'
                            comment_body += comment['body']
                            self.create_comment(dest_owner, dest_repo, new_issue['number'], comment_body)
                            time.sleep(0.5)
                
                print(f'  ✓ 完了: 新しいissue #{new_issue["number"]}')
                time.sleep(1)  # レート制限対策
                
            except Exception as e:
                print(f'  ✗ エラー: {str(e)}')
                continue
        
        print('\n' + '=' * 50)
        print('コピー完了!')


if __name__ == '__main__':
    # 環境変数から設定を取得
    token = os.environ.get('PERSONAL_TOKEN')
    source_owner = os.environ.get('SOURCE_OWNER')
    source_repo = os.environ.get('SOURCE_REPO')
    dest_owner = os.environ.get('DEST_OWNER')
    dest_repo = os.environ.get('DEST_REPO')
    include_comments = os.environ.get('INCLUDE_COMMENTS', 'true').lower() == 'true'
    copy_state = os.environ.get('COPY_STATE', 'true').lower() == 'true'
    
    # 環境変数のチェックと詳細なエラーメッセージ
    missing_vars = []
    if not token:
        missing_vars.append('PERSONAL_TOKEN')
    if not source_owner:
        missing_vars.append('SOURCE_OWNER')
    if not source_repo:
        missing_vars.append('SOURCE_REPO')
    if not dest_owner:
        missing_vars.append('DEST_OWNER')
    if not dest_repo:
        missing_vars.append('DEST_REPO')
    
    if missing_vars:
        print('=' * 60)
        print('エラー: 必要な環境変数が設定されていません')
        print('=' * 60)
        print(f'未設定の変数: {", ".join(missing_vars)}')
        print('\nこのスクリプトは以下の方法で実行してください：\n')
        print('1. GitHub Actionsで実行する場合:')
        print('   - Actionsタブ → "Copy GitHub Issues" → "Run workflow"')
        print('   - フォームに必要な情報を入力して実行\n')
        print('2. ローカルで実行する場合:')
        print('   export PERSONAL_TOKEN="your_token"')
        print('   export SOURCE_OWNER="owner_name"')
        print('   export SOURCE_REPO="repo_name"')
        print('   export DEST_OWNER="owner_name"')
        print('   export DEST_REPO="repo_name"')
        print('   python issues_copy.py\n')
        print('詳細はREADME.mdを参照してください。')
        print('=' * 60)
        exit(1)
    
    print('=' * 60)
    print('GitHub Issues コピーツール')
    print('=' * 60)
    print(f'設定確認:')
    print(f'  コピー元: {source_owner}/{source_repo}')
    print(f'  コピー先: {dest_owner}/{dest_repo}')
    print(f'  コメントをコピー: {"はい" if include_comments else "いいえ"}')
    print(f'  状態を保持: {"はい" if copy_state else "いいえ"}')
    print(f'  トークン: {"設定済み ✓" if token else "未設定 ✗"}')
    print('=' * 60)
    print()
    
    copier = GitHubIssuesCopier(token)
    copier.copy_issues(
        source_owner, source_repo,
        dest_owner, dest_repo,
        include_comments, copy_state
    )
