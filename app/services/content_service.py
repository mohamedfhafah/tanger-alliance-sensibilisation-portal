"""Content Service

This service handles all content-related operations including:
- Content retrieval and formatting
- Content validation
- Dynamic content generation
- Content analytics
"""

from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import re
import json
from app import db
from app.models.module_v2 import ModuleV2, ModuleContentV2
from app.models.module import User


class ContentService:
    """Service for content operations"""
    
    @staticmethod
    def get_module_content(module_id: int, user_id: Optional[int] = None) -> Optional[Dict]:
        """Get formatted content for a module
        
        Args:
            module_id: Module ID
            user_id: User ID (for personalization)
            
        Returns:
            Formatted content dictionary or None
        """
        module = ModuleV2.query.get(module_id)
        if not module or not module.is_active:
            return None
        
        # Get module content
        content_items = ModuleContentV2.query.filter_by(
            module_id=module_id,
            is_active=True
        ).order_by(ModuleContentV2.order).all()
        
        # Format content
        formatted_content = {
            'module': module.to_dict(),
            'sections': []
        }
        
        for content in content_items:
            section = {
                'id': content.id,
                'type': content.content_type,
                'title': content.title,
                'order': content.order,
                'content': ContentService._format_content_by_type(content),
                'metadata': content.metadata or {}
            }
            
            # Add user-specific data if user_id provided
            if user_id:
                section['user_data'] = ContentService._get_user_content_data(user_id, content.id)
            
            formatted_content['sections'].append(section)
        
        return formatted_content
    
    @staticmethod
    def _format_content_by_type(content: ModuleContentV2) -> Dict[str, Any]:
        """Format content based on its type
        
        Args:
            content: ModuleContentV2 object
            
        Returns:
            Formatted content dictionary
        """
        base_content = {
            'raw': content.content,
            'formatted': content.content
        }
        
        if content.content_type == 'text':
            # Process markdown and add formatting
            base_content['formatted'] = ContentService._process_markdown(content.content)
            
        elif content.content_type == 'code':
            # Add syntax highlighting metadata
            language = content.metadata.get('language', 'text') if content.metadata else 'text'
            base_content['language'] = language
            base_content['formatted'] = ContentService._format_code_block(content.content, language)
            
        elif content.content_type == 'interactive':
            # Parse interactive content
            try:
                interactive_data = json.loads(content.content)
                base_content['interactive_data'] = interactive_data
                base_content['formatted'] = ContentService._format_interactive_content(interactive_data)
            except json.JSONDecodeError:
                base_content['error'] = 'Invalid interactive content format'
                
        elif content.content_type == 'video':
            # Process video content
            base_content['video_data'] = ContentService._process_video_content(content.content, content.metadata)
            
        elif content.content_type == 'image':
            # Process image content
            base_content['image_data'] = ContentService._process_image_content(content.content, content.metadata)
            
        elif content.content_type == 'quiz_reference':
            # Reference to quiz content
            base_content['quiz_data'] = ContentService._get_quiz_reference_data(content.content)
        
        return base_content
    
    @staticmethod
    def _process_markdown(content: str) -> str:
        """Process markdown content and add custom formatting
        
        Args:
            content: Raw markdown content
            
        Returns:
            Processed markdown content
        """
        # Add custom processing for security-specific formatting
        processed = content
        
        # Process security alerts
        processed = re.sub(
            r'\[!ALERT\](.+?)\[/ALERT\]',
            r'<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> \1</div>',
            processed,
            flags=re.DOTALL
        )
        
        # Process security tips
        processed = re.sub(
            r'\[!TIP\](.+?)\[/TIP\]',
            r'<div class="alert alert-info"><i class="fas fa-lightbulb"></i> \1</div>',
            processed,
            flags=re.DOTALL
        )
        
        # Process security warnings
        processed = re.sub(
            r'\[!WARNING\](.+?)\[/WARNING\]',
            r'<div class="alert alert-danger"><i class="fas fa-shield-alt"></i> \1</div>',
            processed,
            flags=re.DOTALL
        )
        
        # Process code references
        processed = re.sub(
            r'\[!CODE:([^\]]+)\]',
            r'<code class="inline-code">\1</code>',
            processed
        )
        
        return processed
    
    @staticmethod
    def _format_code_block(content: str, language: str) -> Dict[str, Any]:
        """Format code block with syntax highlighting metadata
        
        Args:
            content: Code content
            language: Programming language
            
        Returns:
            Formatted code block data
        """
        return {
            'code': content,
            'language': language,
            'line_numbers': True,
            'highlight_lines': [],
            'copy_button': True
        }
    
    @staticmethod
    def _format_interactive_content(data: Dict) -> Dict[str, Any]:
        """Format interactive content
        
        Args:
            data: Interactive content data
            
        Returns:
            Formatted interactive content
        """
        content_type = data.get('type', 'unknown')
        
        if content_type == 'simulation':
            return {
                'type': 'simulation',
                'title': data.get('title', 'Security Simulation'),
                'description': data.get('description', ''),
                'scenarios': data.get('scenarios', []),
                'controls': data.get('controls', {})
            }
        
        elif content_type == 'checklist':
            return {
                'type': 'checklist',
                'title': data.get('title', 'Security Checklist'),
                'items': data.get('items', []),
                'allow_user_notes': data.get('allow_notes', True)
            }
        
        elif content_type == 'tool':
            return {
                'type': 'tool',
                'title': data.get('title', 'Security Tool'),
                'tool_type': data.get('tool_type', 'analyzer'),
                'interface': data.get('interface', {}),
                'instructions': data.get('instructions', '')
            }
        
        return data
    
    @staticmethod
    def _process_video_content(content: str, metadata: Optional[Dict]) -> Dict[str, Any]:
        """Process video content
        
        Args:
            content: Video URL or embed code
            metadata: Video metadata
            
        Returns:
            Processed video data
        """
        video_data = {
            'url': content,
            'type': 'url',
            'duration': metadata.get('duration') if metadata else None,
            'thumbnail': metadata.get('thumbnail') if metadata else None,
            'captions': metadata.get('captions', False) if metadata else False
        }
        
        # Detect video platform
        if 'youtube.com' in content or 'youtu.be' in content:
            video_data['platform'] = 'youtube'
            video_data['embed_url'] = ContentService._get_youtube_embed_url(content)
        elif 'vimeo.com' in content:
            video_data['platform'] = 'vimeo'
            video_data['embed_url'] = ContentService._get_vimeo_embed_url(content)
        else:
            video_data['platform'] = 'direct'
            video_data['embed_url'] = content
        
        return video_data
    
    @staticmethod
    def _process_image_content(content: str, metadata: Optional[Dict]) -> Dict[str, Any]:
        """Process image content
        
        Args:
            content: Image URL or path
            metadata: Image metadata
            
        Returns:
            Processed image data
        """
        return {
            'url': content,
            'alt_text': metadata.get('alt_text', '') if metadata else '',
            'caption': metadata.get('caption', '') if metadata else '',
            'width': metadata.get('width') if metadata else None,
            'height': metadata.get('height') if metadata else None,
            'clickable': metadata.get('clickable', False) if metadata else False
        }
    
    @staticmethod
    def _get_quiz_reference_data(content: str) -> Dict[str, Any]:
        """Get quiz reference data
        
        Args:
            content: Quiz reference (quiz ID or identifier)
            
        Returns:
            Quiz reference data
        """
        try:
            quiz_id = int(content)
            from .quiz_service import QuizService
            quiz_data = QuizService.get_quiz_by_module(quiz_id)
            
            return {
                'quiz_id': quiz_id,
                'quiz_available': quiz_data is not None,
                'quiz_title': quiz_data.get('title') if quiz_data else 'Quiz not found'
            }
        except ValueError:
            return {
                'quiz_id': None,
                'quiz_available': False,
                'error': 'Invalid quiz reference'
            }
    
    @staticmethod
    def _get_user_content_data(user_id: int, content_id: int) -> Dict[str, Any]:
        """Get user-specific content data
        
        Args:
            user_id: User ID
            content_id: Content ID
            
        Returns:
            User-specific content data
        """
        # This could include user notes, bookmarks, completion status, etc.
        # For now, return basic structure
        return {
            'viewed': False,  # Track if user has viewed this content
            'bookmarked': False,  # Track if user bookmarked this content
            'notes': '',  # User notes for this content
            'last_accessed': None  # Last access timestamp
        }
    
    @staticmethod
    def _get_youtube_embed_url(url: str) -> str:
        """Convert YouTube URL to embed URL
        
        Args:
            url: YouTube URL
            
        Returns:
            YouTube embed URL
        """
        # Extract video ID from various YouTube URL formats
        patterns = [
            r'youtube\.com/watch\?v=([^&]+)',
            r'youtu\.be/([^?]+)',
            r'youtube\.com/embed/([^?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                return f'https://www.youtube.com/embed/{video_id}'
        
        return url
    
    @staticmethod
    def _get_vimeo_embed_url(url: str) -> str:
        """Convert Vimeo URL to embed URL
        
        Args:
            url: Vimeo URL
            
        Returns:
            Vimeo embed URL
        """
        # Extract video ID from Vimeo URL
        match = re.search(r'vimeo\.com/(\d+)', url)
        if match:
            video_id = match.group(1)
            return f'https://player.vimeo.com/video/{video_id}'
        
        return url
    
    @staticmethod
    def create_content(module_id: int, content_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Create new content for a module
        
        Args:
            module_id: Module ID
            content_data: Content data dictionary
            
        Returns:
            Tuple of (success, message, content_dict)
        """
        # Validate required fields
        required_fields = ['content_type', 'title', 'content']
        for field in required_fields:
            if field not in content_data:
                return False, f"Missing required field: {field}", None
        
        # Validate content type
        valid_types = ['text', 'code', 'interactive', 'video', 'image', 'quiz_reference']
        if content_data['content_type'] not in valid_types:
            return False, f"Invalid content type. Must be one of: {', '.join(valid_types)}", None
        
        # Get next order number
        max_order = db.session.query(
            db.func.max(ModuleContentV2.order)
        ).filter_by(module_id=module_id).scalar() or 0
        
        # Create content
        content = ModuleContentV2(
            module_id=module_id,
            content_type=content_data['content_type'],
            title=content_data['title'],
            content=content_data['content'],
            order=max_order + 1,
            metadata=content_data.get('metadata'),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(content)
        db.session.commit()
        
        return True, "Content created successfully.", content.to_dict()
    
    @staticmethod
    def update_content(content_id: int, content_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """Update existing content
        
        Args:
            content_id: Content ID
            content_data: Updated content data
            
        Returns:
            Tuple of (success, message, content_dict)
        """
        content = ModuleContentV2.query.get(content_id)
        if not content:
            return False, "Content not found.", None
        
        # Update fields if provided
        updatable_fields = ['title', 'content', 'metadata', 'is_active']
        for field in updatable_fields:
            if field in content_data:
                setattr(content, field, content_data[field])
        
        content.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return True, "Content updated successfully.", content.to_dict()
    
    @staticmethod
    def reorder_content(module_id: int, content_orders: List[Dict]) -> Tuple[bool, str]:
        """Reorder content within a module
        
        Args:
            module_id: Module ID
            content_orders: List of {'content_id': int, 'order': int}
            
        Returns:
            Tuple of (success, message)
        """
        try:
            for item in content_orders:
                content = ModuleContentV2.query.filter_by(
                    id=item['content_id'],
                    module_id=module_id
                ).first()
                
                if content:
                    content.order = item['order']
                    content.updated_at = datetime.utcnow()
            
            db.session.commit()
            return True, "Content reordered successfully."
            
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to reorder content: {str(e)}"
    
    @staticmethod
    def delete_content(content_id: int) -> Tuple[bool, str]:
        """Delete content
        
        Args:
            content_id: Content ID
            
        Returns:
            Tuple of (success, message)
        """
        content = ModuleContentV2.query.get(content_id)
        if not content:
            return False, "Content not found."
        
        # Soft delete by setting is_active to False
        content.is_active = False
        content.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return True, "Content deleted successfully."
    
    @staticmethod
    def get_content_analytics(module_id: int) -> Dict:
        """Get analytics for module content
        
        Args:
            module_id: Module ID
            
        Returns:
            Content analytics dictionary
        """
        # Get content statistics
        total_content = ModuleContentV2.query.filter_by(
            module_id=module_id,
            is_active=True
        ).count()
        
        # Count by content type
        content_types = db.session.query(
            ModuleContentV2.content_type,
            db.func.count(ModuleContentV2.id)
        ).filter_by(
            module_id=module_id,
            is_active=True
        ).group_by(ModuleContentV2.content_type).all()
        
        type_distribution = dict(content_types)
        
        # Calculate estimated reading time (rough estimate)
        text_content = ModuleContentV2.query.filter_by(
            module_id=module_id,
            content_type='text',
            is_active=True
        ).all()
        
        total_words = 0
        for content in text_content:
            if content.content:
                total_words += len(content.content.split())
        
        # Assume 200 words per minute reading speed
        estimated_reading_time = max(1, total_words // 200)
        
        return {
            'total_content_items': total_content,
            'content_type_distribution': type_distribution,
            'estimated_reading_time_minutes': estimated_reading_time,
            'total_words': total_words
        }
    
    @staticmethod
    def search_content(query: str, module_id: Optional[int] = None) -> List[Dict]:
        """Search content across modules
        
        Args:
            query: Search query
            module_id: Optional module ID to limit search
            
        Returns:
            List of matching content items
        """
        search_filter = ModuleContentV2.query.filter(
            ModuleContentV2.is_active == True
        )
        
        if module_id:
            search_filter = search_filter.filter_by(module_id=module_id)
        
        # Search in title and content
        search_pattern = f"%{query}%"
        results = search_filter.filter(
            db.or_(
                ModuleContentV2.title.ilike(search_pattern),
                ModuleContentV2.content.ilike(search_pattern)
            )
        ).order_by(ModuleContentV2.module_id, ModuleContentV2.order).all()
        
        return [{
            'content': result.to_dict(),
            'module': result.module.to_dict() if result.module else None,
            'relevance_score': ContentService._calculate_relevance(query, result)
        } for result in results]
    
    @staticmethod
    def _calculate_relevance(query: str, content: ModuleContentV2) -> float:
        """Calculate relevance score for search results
        
        Args:
            query: Search query
            content: Content object
            
        Returns:
            Relevance score (0-1)
        """
        query_lower = query.lower()
        title_lower = content.title.lower() if content.title else ''
        content_lower = content.content.lower() if content.content else ''
        
        score = 0.0
        
        # Title matches are more important
        if query_lower in title_lower:
            score += 0.5
        
        # Content matches
        content_matches = content_lower.count(query_lower)
        if content_matches > 0:
            score += min(0.5, content_matches * 0.1)
        
        return min(1.0, score)