"""
Email tool with A2A, MCP, and SmolAgents compliance.

This tool provides email capabilities while following:
- A2A (Agent-to-Agent) protocol for agent collaboration
- MCP (Multi-Channel Protocol) for unified channel support
- SmolAgents pattern for minimal, efficient implementation
"""

import logging
import asyncio
import aiosmtplib
import aioimaplib
import email
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, Any, List, Optional, Union
from labeeb.core.ai.tool_base import BaseTool

logger = logging.getLogger(__name__)

class EmailTool(BaseTool):
    """Tool for performing email operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the email tool.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(
            name="email",
            description="Tool for performing email operations",
            config=config
        )
        self._smtp_host = config.get('smtp_host')
        self._smtp_port = config.get('smtp_port', 587)
        self._smtp_username = config.get('smtp_username')
        self._smtp_password = config.get('smtp_password')
        self._imap_host = config.get('imap_host')
        self._imap_port = config.get('imap_port', 993)
        self._imap_username = config.get('imap_username')
        self._imap_password = config.get('imap_password')
        self._max_attachments = config.get('max_attachments', 5)
        self._max_attachment_size = config.get('max_attachment_size', 10 * 1024 * 1024)  # 10MB
        self._operation_history = []
        self._max_history = config.get('max_history', 100)
        self._smtp_client = None
        self._imap_client = None
    
    async def initialize(self) -> bool:
        """Initialize the tool.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            # Validate configuration
            if not all([self._smtp_host, self._smtp_username, self._smtp_password]):
                logger.error("SMTP configuration is incomplete")
                return False
            
            if not all([self._imap_host, self._imap_username, self._imap_password]):
                logger.error("IMAP configuration is incomplete")
                return False
            
            # Create SMTP client
            self._smtp_client = aiosmtplib.SMTP(
                hostname=self._smtp_host,
                port=self._smtp_port,
                use_tls=True
            )
            await self._smtp_client.connect()
            await self._smtp_client.login(self._smtp_username, self._smtp_password)
            
            # Create IMAP client
            self._imap_client = aioimaplib.IMAP4_SSL(
                host=self._imap_host,
                port=self._imap_port
            )
            await self._imap_client.wait_hello_from_server()
            await self._imap_client.login(self._imap_username, self._imap_password)
            
            return await super().initialize()
        except Exception as e:
            logger.error(f"Failed to initialize EmailTool: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        try:
            if self._smtp_client:
                await self._smtp_client.quit()
                self._smtp_client = None
            
            if self._imap_client:
                await self._imap_client.logout()
                self._imap_client = None
            
            self._operation_history = []
            await super().cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up EmailTool: {e}")
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this tool.
        
        Returns:
            Dict[str, bool]: Dictionary of capability names and their availability
        """
        base_capabilities = super().get_capabilities()
        tool_capabilities = {
            'send': True,
            'receive': True,
            'search': True,
            'delete': True,
            'history': True
        }
        return {**base_capabilities, **tool_capabilities}
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the tool.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information
        """
        base_status = super().get_status()
        tool_status = {
            'smtp_connected': bool(self._smtp_client),
            'imap_connected': bool(self._imap_client),
            'max_attachments': self._max_attachments,
            'max_attachment_size': self._max_attachment_size,
            'history_size': len(self._operation_history),
            'max_history': self._max_history
        }
        return {**base_status, **tool_status}
    
    async def _execute_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific command.
        
        Args:
            command: Command to execute
            args: Optional arguments for the command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        if command == 'send':
            return await self._send_email(args)
        elif command == 'receive':
            return await self._receive_emails(args)
        elif command == 'search':
            return await self._search_emails(args)
        elif command == 'delete':
            return await self._delete_email(args)
        elif command == 'get_history':
            return await self._get_history()
        elif command == 'clear_history':
            return await self._clear_history()
        else:
            return {'error': f'Unknown command: {command}'}
    
    def _add_to_history(self, operation: str, details: Dict[str, Any]) -> None:
        """Add an operation to history.
        
        Args:
            operation: Operation performed
            details: Operation details
        """
        self._operation_history.append({
            'operation': operation,
            'details': details,
            'timestamp': time.time()
        })
        if len(self._operation_history) > self._max_history:
            self._operation_history.pop(0)
    
    async def _send_email(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send an email.
        
        Args:
            args: Email arguments
            
        Returns:
            Dict[str, Any]: Result of send operation
        """
        try:
            if not args or 'to' not in args or 'subject' not in args or 'body' not in args:
                return {'error': 'Missing required email parameters'}
            
            to = args['to']
            subject = args['subject']
            body = args['body']
            cc = args.get('cc', [])
            bcc = args.get('bcc', [])
            attachments = args.get('attachments', [])
            
            # Validate attachments
            if len(attachments) > self._max_attachments:
                return {'error': f'Too many attachments (max: {self._max_attachments})'}
            
            for attachment in attachments:
                if attachment.get('size', 0) > self._max_attachment_size:
                    return {'error': f'Attachment too large (max: {self._max_attachment_size} bytes)'}
            
            # Create message
            message = MIMEMultipart()
            message['From'] = self._smtp_username
            message['To'] = ', '.join(to)
            if cc:
                message['Cc'] = ', '.join(cc)
            if bcc:
                message['Bcc'] = ', '.join(bcc)
            message['Subject'] = subject
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            for attachment in attachments:
                part = MIMEApplication(attachment['data'])
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=attachment['filename']
                )
                message.attach(part)
            
            # Send email
            await self._smtp_client.send_message(
                message,
                to_addrs=to + cc + bcc
            )
            
            result = {
                'status': 'success',
                'action': 'send',
                'to': to,
                'subject': subject,
                'attachment_count': len(attachments)
            }
            
            self._add_to_history('send', {
                'to': to,
                'subject': subject,
                'attachment_count': len(attachments)
            })
            
            return result
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {'error': str(e)}
    
    async def _receive_emails(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Receive emails.
        
        Args:
            args: Receive arguments
            
        Returns:
            Dict[str, Any]: Result of receive operation
        """
        try:
            folder = args.get('folder', 'INBOX')
            limit = args.get('limit', 10)
            
            # Select folder
            await self._imap_client.select(folder)
            
            # Search for all messages
            _, message_numbers = await self._imap_client.search('ALL')
            message_numbers = message_numbers[0].split()
            
            # Get the most recent messages
            messages = []
            for num in message_numbers[-limit:]:
                _, msg_data = await self._imap_client.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Parse message
                message = {
                    'id': num.decode(),
                    'from': email_message['from'],
                    'to': email_message['to'],
                    'subject': email_message['subject'],
                    'date': email_message['date'],
                    'body': '',
                    'attachments': []
                }
                
                # Get body and attachments
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == 'text/plain':
                            message['body'] = part.get_payload(decode=True).decode()
                        elif part.get_content_maintype() == 'application':
                            message['attachments'].append({
                                'filename': part.get_filename(),
                                'content_type': part.get_content_type(),
                                'size': len(part.get_payload(decode=True))
                            })
                else:
                    message['body'] = email_message.get_payload(decode=True).decode()
                
                messages.append(message)
            
            result = {
                'status': 'success',
                'action': 'receive',
                'folder': folder,
                'messages': messages
            }
            
            self._add_to_history('receive', {
                'folder': folder,
                'message_count': len(messages)
            })
            
            return result
        except Exception as e:
            logger.error(f"Error receiving emails: {e}")
            return {'error': str(e)}
    
    async def _search_emails(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search emails.
        
        Args:
            args: Search arguments
            
        Returns:
            Dict[str, Any]: Result of search operation
        """
        try:
            if not args or 'query' not in args:
                return {'error': 'Missing search query'}
            
            query = args['query']
            folder = args.get('folder', 'INBOX')
            limit = args.get('limit', 10)
            
            # Select folder
            await self._imap_client.select(folder)
            
            # Search for messages
            search_criteria = f'(SUBJECT "{query}" OR FROM "{query}" OR TO "{query}")'
            _, message_numbers = await self._imap_client.search(search_criteria)
            message_numbers = message_numbers[0].split()
            
            # Get the matching messages
            messages = []
            for num in message_numbers[-limit:]:
                _, msg_data = await self._imap_client.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Parse message
                message = {
                    'id': num.decode(),
                    'from': email_message['from'],
                    'to': email_message['to'],
                    'subject': email_message['subject'],
                    'date': email_message['date'],
                    'body': '',
                    'attachments': []
                }
                
                # Get body and attachments
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == 'text/plain':
                            message['body'] = part.get_payload(decode=True).decode()
                        elif part.get_content_maintype() == 'application':
                            message['attachments'].append({
                                'filename': part.get_filename(),
                                'content_type': part.get_content_type(),
                                'size': len(part.get_payload(decode=True))
                            })
                else:
                    message['body'] = email_message.get_payload(decode=True).decode()
                
                messages.append(message)
            
            result = {
                'status': 'success',
                'action': 'search',
                'query': query,
                'folder': folder,
                'messages': messages
            }
            
            self._add_to_history('search', {
                'query': query,
                'folder': folder,
                'message_count': len(messages)
            })
            
            return result
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return {'error': str(e)}
    
    async def _delete_email(self, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete an email.
        
        Args:
            args: Delete arguments
            
        Returns:
            Dict[str, Any]: Result of delete operation
        """
        try:
            if not args or 'message_id' not in args:
                return {'error': 'Missing message ID'}
            
            message_id = args['message_id']
            folder = args.get('folder', 'INBOX')
            
            # Select folder
            await self._imap_client.select(folder)
            
            # Delete message
            await self._imap_client.store(message_id, '+FLAGS', '\\Deleted')
            await self._imap_client.expunge()
            
            result = {
                'status': 'success',
                'action': 'delete',
                'message_id': message_id,
                'folder': folder
            }
            
            self._add_to_history('delete', {
                'message_id': message_id,
                'folder': folder
            })
            
            return result
        except Exception as e:
            logger.error(f"Error deleting email: {e}")
            return {'error': str(e)}
    
    async def _get_history(self) -> Dict[str, Any]:
        """Get operation history.
        
        Returns:
            Dict[str, Any]: Operation history
        """
        try:
            return {
                'status': 'success',
                'action': 'get_history',
                'history': self._operation_history
            }
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return {'error': str(e)}
    
    async def _clear_history(self) -> Dict[str, Any]:
        """Clear operation history.
        
        Returns:
            Dict[str, Any]: Result of clearing history
        """
        try:
            self._operation_history = []
            return {
                'status': 'success',
                'action': 'clear_history'
            }
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return {'error': str(e)} 