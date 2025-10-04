#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.

import json
import logging
import unittest
from unittest.mock import Mock, patch

# Import module under test
from wit.pywit.source.wit.wit import req, Wit, WitError


class WitErrorTestCase(unittest.TestCase):
    def test_wit_error_constructor_creates_instance(self) -> None:
        # Arrange
        error_message = "Test error message"

        # Act
        error = WitError(error_message)

        # Assert
        self.assertEqual(str(error), error_message)
        self.assertIsInstance(error, Exception)


class ReqFunctionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_logger = Mock()
        self.access_token = "test_access_token"
        self.meth = "GET"
        self.path = "/test/path"
        self.params = {"param1": "value1"}

    @patch("wit.pywit.source.wit.wit.requests.request")
    def test_req_with_successful_response_returns_json(
        self, mock_request: Mock
    ) -> None:
        # Arrange
        expected_json = {"result": "success", "data": {"key": "value"}}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_json
        mock_request.return_value = mock_response

        # Act
        result = req(
            self.mock_logger, self.access_token, self.meth, self.path, self.params
        )

        # Assert
        self.assertEqual(result, expected_json)
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], self.meth)
        self.assertIn("https://api.wit.ai/test/path", call_args[0][1])
        self.assertIn("authorization", call_args[1]["headers"])
        self.assertEqual(
            call_args[1]["headers"]["authorization"], f"Bearer {self.access_token}"
        )

    @patch("wit.pywit.source.wit.wit.requests.request")
    def test_req_with_http_error_raises_wit_error(self, mock_request: Mock) -> None:
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_request.return_value = mock_response

        # Act & Assert
        with self.assertRaises(WitError) as context:
            req(self.mock_logger, self.access_token, self.meth, self.path, self.params)

        self.assertIn("404", str(context.exception))
        self.assertIn("Not Found", str(context.exception))

    @patch("wit.pywit.source.wit.wit.requests.request")
    def test_req_with_api_error_raises_wit_error(self, mock_request: Mock) -> None:
        # Arrange
        error_response = {"error": "Invalid access token"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = error_response
        mock_request.return_value = mock_response

        # Act & Assert
        with self.assertRaises(WitError) as context:
            req(self.mock_logger, self.access_token, self.meth, self.path, self.params)

        self.assertIn("Invalid access token", str(context.exception))

    @patch("wit.pywit.source.wit.wit.requests.request")
    def test_req_with_custom_headers_includes_headers(self, mock_request: Mock) -> None:
        # Arrange
        expected_json = {"result": "success"}
        custom_headers = {"Custom-Header": "custom_value"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_json
        mock_request.return_value = mock_response

        # Act
        result = req(
            self.mock_logger,
            self.access_token,
            self.meth,
            self.path,
            self.params,
            headers=custom_headers,
        )

        # Assert
        self.assertEqual(result, expected_json)
        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        self.assertIn("Custom-Header", headers)
        self.assertEqual(headers["Custom-Header"], "custom_value")
        self.assertIn("authorization", headers)

    @patch("wit.pywit.source.wit.wit.WIT_API_HOST", "https://test.wit.ai")
    @patch("wit.pywit.source.wit.wit.WIT_API_VERSION", "20210101")
    @patch("wit.pywit.source.wit.wit.requests.request")
    def test_req_with_environment_variables_uses_custom_config(
        self, mock_request: Mock
    ) -> None:
        # Arrange
        expected_json = {"result": "success"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_json
        mock_request.return_value = mock_response

        # Act
        result = req(
            self.mock_logger, self.access_token, self.meth, self.path, self.params
        )

        # Assert
        self.assertEqual(result, expected_json)
        call_args = mock_request.call_args
        self.assertIn("https://test.wit.ai/test/path", call_args[0][1])
        headers = call_args[1]["headers"]
        self.assertIn("application/vnd.wit.20210101+json", headers["accept"])


class WitTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.access_token = "test_access_token_12345"
        self.mock_logger = Mock()
        self.wit_client = Wit(access_token=self.access_token, logger=self.mock_logger)

    def test_constructor_with_access_token_creates_instance(self) -> None:
        # Act
        client = Wit(access_token=self.access_token)

        # Assert
        self.assertIsNotNone(client)
        self.assertEqual(client.access_token, self.access_token)
        self.assertIsNotNone(client.logger)

    def test_constructor_with_custom_logger_uses_logger(self) -> None:
        # Arrange
        custom_logger = logging.getLogger("custom_test_logger")

        # Act
        client = Wit(access_token=self.access_token, logger=custom_logger)

        # Assert
        self.assertEqual(client.logger, custom_logger)

    @patch("wit.pywit.source.wit.wit.req")
    def test_message_with_text_calls_api_correctly(self, mock_req: Mock) -> None:
        # Arrange
        message_text = "Hello world"
        expected_response = {"text": message_text, "intents": [], "entities": {}}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.message(message_text)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger, self.access_token, "GET", "/message", {"q": message_text}
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_message_with_context_includes_context_in_params(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        message_text = "Book a flight"
        context = {"timezone": "America/Los_Angeles", "locale": "en_US"}
        expected_response = {"text": message_text, "intents": [], "entities": {}}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.message(message_text, context=context)

        # Assert
        self.assertEqual(result, expected_response)
        expected_params = {"q": message_text, "context": json.dumps(context)}
        mock_req.assert_called_once_with(
            self.mock_logger, self.access_token, "GET", "/message", expected_params
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_message_with_n_parameter_includes_n_in_params(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        message_text = "Find restaurants"
        n_value = 5
        expected_response = {"text": message_text, "intents": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.message(message_text, n=n_value)

        # Assert
        self.assertEqual(result, expected_response)
        expected_params = {"q": message_text, "n": n_value}
        mock_req.assert_called_once_with(
            self.mock_logger, self.access_token, "GET", "/message", expected_params
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_message_with_verbose_includes_verbose_in_params(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        message_text = "What's the weather?"
        verbose = True
        expected_response = {"text": message_text, "intents": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.message(message_text, verbose=verbose)

        # Assert
        self.assertEqual(result, expected_response)
        expected_params = {"q": message_text, "verbose": verbose}
        mock_req.assert_called_once_with(
            self.mock_logger, self.access_token, "GET", "/message", expected_params
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_message_with_empty_text_excludes_q_parameter(self, mock_req: Mock) -> None:
        # Arrange
        expected_response = {"intents": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.message("")

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger, self.access_token, "GET", "/message", {}
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_speech_with_audio_file_calls_api_correctly(self, mock_req: Mock) -> None:
        # Arrange
        mock_audio_file = Mock()
        expected_response = {"text": "Hello world", "intents": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.speech(mock_audio_file)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/speech",
            {},
            data=mock_audio_file,
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_speech_with_custom_headers_includes_headers(self, mock_req: Mock) -> None:
        # Arrange
        mock_audio_file = Mock()
        custom_headers = {"Content-Type": "audio/wav"}
        expected_response = {"text": "Hello world", "intents": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.speech(mock_audio_file, headers=custom_headers)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/speech",
            {},
            data=mock_audio_file,
            headers=custom_headers,
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_speech_with_verbose_includes_verbose_in_params(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        mock_audio_file = Mock()
        expected_response = {"text": "Hello world", "intents": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.speech(mock_audio_file, verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/speech",
            {"verbose": True},
            data=mock_audio_file,
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.prompt")
    def test_interactive_with_default_handler_prints_responses(
        self, mock_prompt: Mock
    ) -> None:
        # Arrange
        mock_prompt.side_effect = ["Hello", "Goodbye", EOFError()]

        with patch.object(self.wit_client, "message") as mock_message:
            mock_message.side_effect = [
                {"text": "Hello", "intents": []},
                {"text": "Goodbye", "intents": []},
            ]

            with patch("builtins.print") as mock_print:
                # Act
                self.wit_client.interactive()

                # Assert
                self.assertEqual(mock_message.call_count, 2)
                mock_message.assert_any_call("Hello", {})
                mock_message.assert_any_call("Goodbye", {})
                self.assertEqual(mock_print.call_count, 2)

    @patch("wit.pywit.source.wit.wit.prompt")
    def test_interactive_with_keyboard_interrupt_exits_gracefully(
        self, mock_prompt: Mock
    ) -> None:
        # Arrange
        mock_prompt.side_effect = KeyboardInterrupt()

        # Act
        result = self.wit_client.interactive()

        # Assert
        self.assertIsNone(result)

    @patch("wit.pywit.source.wit.wit.prompt")
    def test_interactive_with_custom_handler_uses_handler(
        self, mock_prompt: Mock
    ) -> None:
        # Arrange
        mock_prompt.side_effect = ["Hello", EOFError()]
        custom_handler = Mock(return_value="Custom response")

        with patch.object(self.wit_client, "message") as mock_message:
            mock_message.return_value = {"text": "Hello", "intents": []}

            with patch("builtins.print") as mock_print:
                # Act
                self.wit_client.interactive(handle_message=custom_handler)

                # Assert
                mock_message.assert_called_once_with("Hello", {})
                custom_handler.assert_called_once_with({"text": "Hello", "intents": []})
                mock_print.assert_called_once_with("Custom response")

    @patch("wit.pywit.source.wit.wit.req")
    def test_intent_list_calls_api_correctly(self, mock_req: Mock) -> None:
        # Arrange
        expected_response = {"intents": ["greetings", "goodbye"]}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.intent_list()

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger, self.access_token, "GET", "/intents", {}, headers={}
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_intent_list_with_verbose_includes_verbose_in_params(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        expected_response = {"intents": ["greetings", "goodbye"]}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.intent_list(verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/intents",
            {"verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_detect_language_with_message_calls_api_correctly(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        message_text = "Bonjour le monde"
        expected_response = {"detected_locales": [{"locale": "fr", "confidence": 0.95}]}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.detect_language(message_text)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/language",
            {"q": message_text},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_detect_language_with_n_parameter_includes_n_in_params(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        message_text = "Hello world"
        n_value = 3
        expected_response = {"detected_locales": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.detect_language(message_text, n=n_value)

        # Assert
        self.assertEqual(result, expected_response)
        expected_params = {"q": message_text, "n": n_value}
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/language",
            expected_params,
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_intent_info_calls_api_with_encoded_intent_name(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        intent_name = "greetings/hello"
        expected_response = {"name": intent_name, "entities": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.intent_info(intent_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/intents/greetings%2Fhello",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_entity_list_calls_api_correctly(self, mock_req: Mock) -> None:
        # Arrange
        expected_response = {"entities": ["location", "datetime"]}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.entity_list()

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger, self.access_token, "GET", "/entities", {}, headers={}
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_entity_info_calls_api_with_encoded_entity_name(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        entity_name = "location/city"
        expected_response = {"name": entity_name, "values": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.entity_info(entity_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/entities/location%2Fcity",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_trait_list_calls_api_correctly(self, mock_req: Mock) -> None:
        # Arrange
        expected_response = {"traits": ["sentiment", "greetings"]}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.trait_list()

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger, self.access_token, "GET", "/traits", {}, headers={}
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_trait_info_calls_api_with_encoded_trait_name(self, mock_req: Mock) -> None:
        # Arrange
        trait_name = "sentiment/positive"
        expected_response = {"name": trait_name, "values": []}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.trait_info(trait_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/traits/sentiment%2Fpositive",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_intent_calls_api_with_encoded_intent_name(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        intent_name = "greetings/hello"
        expected_response = {"deleted": intent_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_intent(intent_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/intents/greetings%2Fhello",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_entity_calls_api_with_encoded_entity_name(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        entity_name = "location/city"
        expected_response = {"deleted": entity_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_entity(entity_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/entities/location%2Fcity",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_role_calls_api_with_encoded_names(self, mock_req: Mock) -> None:
        # Arrange
        entity_name = "location/city"
        role_name = "from_location"
        expected_response = {"deleted": f"{entity_name}:{role_name}"}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_role(entity_name, role_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/entities/location%2Fcity:from_location",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_keyword_calls_api_with_encoded_names(self, mock_req: Mock) -> None:
        # Arrange
        entity_name = "location/city"
        keyword_name = "paris"
        expected_response = {"deleted": f"{entity_name}/keywords/{keyword_name}"}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_keyword(entity_name, keyword_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/entities/location%2Fcity/keywords/paris",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_synonym_calls_api_with_encoded_names(self, mock_req: Mock) -> None:
        # Arrange
        entity_name = "location/city"
        keyword_name = "paris"
        synonym_name = "city of light"
        expected_response = {
            "deleted": f"{entity_name}/keywords/{keyword_name}/synonyms/{synonym_name}"
        }
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_synonym(entity_name, keyword_name, synonym_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/entities/location%2Fcity/keywords/paris/synonyms/city%20of%20light",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_trait_calls_api_with_encoded_trait_name(
        self, mock_req: Mock
    ) -> None:
        # Arrange
        trait_name = "sentiment/positive"
        expected_response = {"deleted": trait_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_trait(trait_name)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/traits/sentiment%2Fpositive",
            {},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_trait_value(self, mock_req: Mock) -> None:
        # Arrange
        trait_name = "sentiment/positive"
        trait_value = "city"
        expected_response = {"deleted": trait_value}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_trait_value(
            trait_name, trait_value, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/traits/sentiment%2Fpositive/values/city",
            {"verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_get_utterances(self, mock_req: Mock) -> None:
        # Arrange
        expected_response = {"utterances": ["tell joke"]}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.get_utterances(
            limit=10, offset=20, intents=["tell_joke"], headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/utterances",
            {"limit": 10, "offset": 20, "intents": ["tell_joke"], "verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_utterances(self, mock_req: Mock) -> None:
        # Arrange
        utterances = ["tell joke", "tell me a joke"]
        expected_response = {"deleted": True}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_utterances(
            utterances=utterances, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/utterances",
            {"verbose": True},
            json=[{"text": "tell joke"}, {"text": "tell me a joke"}],
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_get_apps(self, mock_req: Mock) -> None:
        # Arrange
        expected_response = {"apps": [1, 2]}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.get_apps(limit=10, offset=20, headers={}, verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/apps",
            {"limit": 10, "offset": 20, "verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_app_info(self, mock_req: Mock) -> None:
        # Arrange
        app_id = "123"
        expected_response = {"app": "app_info"}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.app_info(app_id, headers={}, verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/apps/123",
            {"verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_app(self, mock_req: Mock) -> None:
        # Arrange
        app_id = "123"
        expected_response = {"deleted": 123}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_app(app_id, headers={}, verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/apps/123",
            {"verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_app_versions(self, mock_req: Mock) -> None:
        # Arrange
        app_id = "123"
        expected_response = {"app_versions": "versions"}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.app_versions(app_id, headers={}, verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/apps/123/tags",
            {"verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_app_version_info(self, mock_req: Mock) -> None:
        # Arrange
        app_id = "123"
        tag_id = "v1"
        expected_response = {"app_version": "version"}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.app_version_info(
            app_id, tag_id, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/apps/123/tags/v1",
            {"verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_create_app_version(self, mock_req: Mock) -> None:
        # Arrange
        app_id = "123"
        tag_name = "v2.0"
        expected_response = {"tag": tag_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.create_app_version(
            app_id, tag_name, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/apps/123/tags/",
            {"verbose": True},
            json={"tag": tag_name},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_delete_app_version(self, mock_req: Mock) -> None:
        # Arrange
        app_id = "123"
        tag_name = "v1.0"
        expected_response = {"deleted": tag_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.delete_app_version(
            app_id, tag_name, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "DELETE",
            "/apps/123/tags/v1.0",
            {"verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_export(self, mock_req: Mock) -> None:
        # Arrange
        expected_response = {"url": "https://example.com/export.zip"}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.export(headers={}, verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "GET",
            "/export",
            {"verbose": True},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_import_app(self, mock_req: Mock) -> None:
        # Arrange
        name = "TestApp"
        private = True
        zip_file = Mock()
        expected_response = {"app_id": 456}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.import_app(
            name, private, zip_file, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/import",
            {"name": name, "private": private, "verbose": True},
            data=zip_file,
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_create_intent(self, mock_req: Mock) -> None:
        # Arrange
        intent_name = "greetings"
        expected_response = {"name": intent_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.create_intent(intent_name, headers={}, verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/intents",
            {"verbose": True},
            json={"name": intent_name},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_create_entity(self, mock_req: Mock) -> None:
        # Arrange
        entity_name = "location"
        roles = ["from", "to"]
        lookups = ["free-text", "keywords"]
        expected_response = {"name": entity_name, "roles": roles}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.create_entity(
            entity_name, roles, lookups=lookups, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/entities",
            {"verbose": True},
            json={"name": entity_name, "roles": roles, "lookups": lookups},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_update_entity(self, mock_req: Mock) -> None:
        # Arrange
        current_entity_name = "location"
        new_entity_name = "location_updated"
        roles = ["from", "to", "via"]
        lookups = ["free-text"]
        expected_response = {"name": new_entity_name, "roles": roles}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.update_entity(
            current_entity_name,
            new_entity_name,
            roles,
            lookups=lookups,
            headers={},
            verbose=True,
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "PUT",
            "/entities/location",
            {"verbose": True},
            json={"name": new_entity_name, "roles": roles, "lookups": lookups},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_add_keyword_value(self, mock_req: Mock) -> None:
        # Arrange
        entity_name = "location"
        data = {"keyword": "paris", "synonyms": ["city of light"]}
        expected_response = {"keyword": "paris"}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.add_keyword_value(
            entity_name, data, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/entities/location/keywords",
            {"verbose": True},
            json=data,
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_create_synonym(self, mock_req: Mock) -> None:
        # Arrange
        entity_name = "location"
        keyword_name = "paris"
        synonym = "city of light"
        expected_response = {"synonym": synonym}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.create_synonym(
            entity_name, keyword_name, synonym, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/entities/location/keywords/paris/synonyms",
            {"verbose": True},
            json={"synonym": synonym},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_create_trait(self, mock_req: Mock) -> None:
        # Arrange
        trait_name = "sentiment"
        values = ["positive", "negative", "neutral"]
        expected_response = {"name": trait_name, "values": values}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.create_trait(
            trait_name, values, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/traits",
            {"verbose": True},
            json={"name": trait_name, "values": values},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_create_trait_value(self, mock_req: Mock) -> None:
        # Arrange
        trait_name = "sentiment"
        new_value = "mixed"
        expected_response = {"value": new_value}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.create_trait_value(
            trait_name, new_value, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/traits/sentiment/values",
            {"verbose": True},
            json={"value": new_value},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_train(self, mock_req: Mock) -> None:
        # Arrange
        data = [{"text": "hello", "intent": "greetings"}]
        expected_response = {"n": 1, "sent": True}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.train(data, headers={}, verbose=True)

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/utterances",
            {"verbose": True},
            json=data,
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_create_app(self, mock_req: Mock) -> None:
        # Arrange
        app_name = "TestApp"
        lang = "en"
        private = True
        timezone = "America/Los_Angeles"
        expected_response = {"app_id": 789, "name": app_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.create_app(
            app_name, lang, private, timezone=timezone, headers={}, verbose=True
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "POST",
            "/apps",
            {"timezone": timezone, "verbose": True},
            json={"name": app_name, "lang": lang, "private": private},
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_update_app(self, mock_req: Mock) -> None:
        # Arrange
        app_id = "123"
        app_name = "UpdatedApp"
        lang = "es"
        private = (
            True  # Changed to True since the implementation only includes truthy values
        )
        timezone = "Europe/Madrid"
        expected_response = {"app_id": app_id, "name": app_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.update_app(
            app_id,
            app_name=app_name,
            lang=lang,
            private=private,
            timezone=timezone,
            headers={},
            verbose=True,
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "PUT",
            "/apps/123",
            {"verbose": True},
            json={
                "name": app_name,
                "lang": lang,
                "private": private,
                "timezone": timezone,
            },
            headers={},
        )

    @patch("wit.pywit.source.wit.wit.req")
    def test_update_app_version(self, mock_req: Mock) -> None:
        # Arrange
        app_id = "123"
        tag_name = "v1.0"
        new_name = "v1.1"
        desc = "Updated version with bug fixes"
        move_to = "v2.0"
        expected_response = {"tag": new_name}
        mock_req.return_value = expected_response

        # Act
        result = self.wit_client.update_app_version(
            app_id,
            tag_name,
            new_name=new_name,
            desc=desc,
            move_to=move_to,
            headers={},
            verbose=True,
        )

        # Assert
        self.assertEqual(result, expected_response)
        mock_req.assert_called_once_with(
            self.mock_logger,
            self.access_token,
            "PUT",
            "/apps/123/tags/v1.0",
            {"verbose": True},
            json={"tag": new_name, "desc": desc, "move_to": move_to},
            headers={},
        )

    def test_wit_class_has_expected_class_variables(self) -> None:
        # Assert
        self.assertIsNone(Wit.access_token)
        self.assertIsInstance(Wit._sessions, dict)
        self.assertEqual(Wit._sessions, {})


if __name__ == "__main__":
    unittest.main()
