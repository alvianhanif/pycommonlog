import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import unittest
from unittest.mock import Mock, patch
from pycommonlog.log_types import Config, SendMethod, AlertLevel, Attachment
from pycommonlog.logger import commonlog

class Testcommonlog(unittest.TestCase):
    def test_init(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        self.assertEqual(logger.config.provider, "slack")

    def test_init_with_lark(self):
        config = Config(
            provider="lark",
            send_method=SendMethod.WEBHOOK,
            lark_token=Mock(app_id="test", app_secret="secret"),
            channel="test-channel"
        )
        logger = commonlog(config)
        self.assertEqual(logger.config.provider, "lark")

    def test_init_with_unknown_provider(self):
        config = Config(
            provider="unknown",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        self.assertEqual(logger.config.provider, "unknown")
        # Should default to slack provider
        self.assertIsNotNone(logger.provider)

    def test_send_info(self):
        config = Config(provider="slack", send_method=SendMethod.WEBCLIENT)
        logger = commonlog(config)
        # INFO should not send
        logger.send(AlertLevel.INFO, "Test info", trace="")

    def test_send_warn(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        # Mock the provider to avoid actual API calls
        with patch.object(logger.provider, 'send') as mock_send:
            logger.send(AlertLevel.WARN, "Test warn message")
            mock_send.assert_called_once()

    def test_send_error(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        # Mock the provider to avoid actual API calls
        with patch.object(logger.provider, 'send') as mock_send:
            logger.send(AlertLevel.ERROR, "Test error message")
            mock_send.assert_called_once()

    def test_send_to_channel(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#default"
        )
        logger = commonlog(config)
        # Mock the provider to avoid actual API calls
        with patch.object(logger.provider, 'send_to_channel') as mock_send:
            logger.send_to_channel(AlertLevel.WARN, "Test message", channel="#custom")
            mock_send.assert_called_once()

    def test_send_with_attachment(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        attachment = Attachment(file_name="test.txt", content="test content")
        # Mock the provider to avoid actual API calls
        with patch.object(logger.provider, 'send') as mock_send:
            logger.send(AlertLevel.ERROR, "Test with attachment", attachment=attachment)
            mock_send.assert_called_once()

    def test_send_with_trace(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        trace = "stack trace here"
        # Mock the provider to avoid actual API calls
        with patch.object(logger.provider, 'send') as mock_send:
            logger.send(AlertLevel.ERROR, "Test with trace", trace=trace)
            mock_send.assert_called_once()

    def test_send_with_attachment_and_trace(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        attachment = Attachment(file_name="test.txt", content="test content")
        trace = "stack trace here"
        # Mock the provider to avoid actual API calls
        with patch.object(logger.provider, 'send') as mock_send:
            logger.send(AlertLevel.ERROR, "Test with attachment and trace", attachment=attachment, trace=trace)
            mock_send.assert_called_once()

    def test_send_to_channel_with_trace(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        trace = "stack trace here"
        # Mock the provider to avoid actual API calls
        with patch.object(logger.provider, 'send_to_channel') as mock_send:
            logger.send_to_channel(AlertLevel.ERROR, "Test with trace", trace=trace, channel="#custom")
            mock_send.assert_called_once()

    def test_custom_send(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        # Mock the LarkProvider.send method to avoid Redis connection
        with patch('pycommonlog.providers.LarkProvider.send') as mock_send:
            logger.custom_send("lark", AlertLevel.ERROR, "Custom provider test")
            mock_send.assert_called_once()

    def test_custom_send_unknown_provider(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        # Should default to Slack for unknown provider without raising exception
        with patch('pycommonlog.providers.SlackProvider.send') as mock_send:
            logger.custom_send("unknown", AlertLevel.ERROR, "Unknown provider test")
            mock_send.assert_called_once()

    def test_resolve_channel_with_resolver(self):
        from pycommonlog.log_types import DefaultChannelResolver
        resolver = DefaultChannelResolver(
            channel_map={AlertLevel.ERROR: "#errors", AlertLevel.WARN: "#warnings"},
            default_channel="#general"
        )
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#default",
            channel_resolver=resolver
        )
        logger = commonlog(config)

        # Test ERROR level resolution
        error_channel = logger._resolve_channel(AlertLevel.ERROR)
        self.assertEqual(error_channel, "#errors")

        # Test WARN level resolution
        warn_channel = logger._resolve_channel(AlertLevel.WARN)
        self.assertEqual(warn_channel, "#warnings")

        # Test INFO level resolution (should use default)
        info_channel = logger._resolve_channel(AlertLevel.INFO)
        self.assertEqual(info_channel, "#general")

    def test_resolve_channel_without_resolver(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#default"
        )
        logger = commonlog(config)

        channel = logger._resolve_channel(AlertLevel.ERROR)
        self.assertEqual(channel, "#default")

    def test_send_error_handling(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        # Mock the provider to raise an exception
        with patch.object(logger.provider, 'send', side_effect=Exception("Test error")):
            with self.assertRaises(Exception):
                logger.send(AlertLevel.ERROR, "Test message")

    def test_send_to_channel_error_handling(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        # Mock the provider to raise an exception
        with patch.object(logger.provider, 'send_to_channel', side_effect=Exception("Test error")):
            with self.assertRaises(Exception):
                logger.send_to_channel(AlertLevel.ERROR, "Test message", channel="#custom")

    def test_custom_send_error_handling(self):
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            channel="#test"
        )
        logger = commonlog(config)
        # Mock the provider to raise an exception
        with patch('pycommonlog.providers.LarkProvider.send', side_effect=Exception("Test error")):
            with self.assertRaises(Exception):
                logger.custom_send("lark", AlertLevel.ERROR, "Test message")

    def test_provider_config_population(self):
        from pycommonlog.log_types import LarkToken
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="dummy-token",
            slack_token="slack-specific-token",
            lark_token=LarkToken(app_id="test", app_secret="secret"),
            channel="#test"
        )
        logger = commonlog(config)

        # Check that provider_config is populated with top-level fields
        self.assertEqual(logger.config.provider_config["provider"], "slack")
        self.assertEqual(logger.config.provider_config["token"], "dummy-token")
        self.assertEqual(logger.config.provider_config["slack_token"], "slack-specific-token")
        self.assertEqual(logger.config.provider_config["lark_token"].app_id, "test")
        self.assertEqual(logger.config.provider_config["lark_token"].app_secret, "secret")

    def test_provider_config_usage(self):
        # Test that providers use provider_config instead of top-level fields
        config = Config(
            provider="slack",
            send_method=SendMethod.WEBCLIENT,
            token="old-token",
            slack_token="new-slack-token",
            channel="#test",
            provider_config={
                "token": "provider-config-token",
                "slack_token": "provider-config-slack-token",
            }
        )
        logger = commonlog(config)

        # Since we populate in Config.__init__, it should override provider_config with top-level
        self.assertEqual(logger.config.provider_config["token"], "old-token")
        self.assertEqual(logger.config.provider_config["slack_token"], "new-slack-token")

    def test_provider_config_only(self):
        from pycommonlog.log_types import LarkToken
        # Test that provider_config can be used without top-level fields
        config = Config(
            provider="",  # empty top-level
            send_method=SendMethod.WEBCLIENT,
            channel="#test",
            provider_config={
                "provider": "lark",
                "token": "config-token",
                "slack_token": "config-slack-token",
                "lark_token": LarkToken(app_id="config-app", app_secret="config-secret"),
            }
        )
        logger = commonlog(config)

        # Check that provider_config values are used
        self.assertEqual(logger.config.provider_config["provider"], "lark")
        self.assertEqual(logger.config.provider_config["token"], "config-token")
        self.assertEqual(logger.config.provider_config["lark_token"].app_id, "config-app")

        # Verify the logger uses the provider from provider_config
        self.assertIsNotNone(logger.provider)

if __name__ == '__main__':
    unittest.main()