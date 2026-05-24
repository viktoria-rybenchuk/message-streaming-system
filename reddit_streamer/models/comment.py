from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class Comment:
    comment_id: str
    comment_text: str
    comment_link_id: str
    subreddit: str
    category: str
    timestamp: str
    author: str
    score: str
    ups: str
    parent_id: str
    link_id: str

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'Comment':
        return cls(
            comment_id=row.get('0', ''),
            comment_text=row.get('1', ''),
            comment_link_id=row.get('2', ''),
            subreddit=row.get('3', 'progresspics'),
            category=row.get('4', 'lifestyle'),
            timestamp=row.get('5', ''),
            author=row.get('6', ''),
            score=row.get('7', '0'),
            ups=row.get('8', '0'),
            parent_id=row.get('9', ''),
            link_id=row.get('10', '')
        )

    def to_message(self) -> Dict[str, Any]:
        return {
            'comment_id': self.comment_id,
            'comment_text': self.comment_text,
            'comment_link_id': self.comment_link_id,
            'subreddit': self.subreddit,
            'category': self.category,
            'timestamp': self.timestamp,
            'author': self.author,
            'score': self.score,
            'ups': self.ups,
            'parent_id': self.parent_id,
            'link_id': self.link_id,
            'sent_timestamp': datetime.now().isoformat()
        }