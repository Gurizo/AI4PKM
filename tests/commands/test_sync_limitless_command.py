import pytest
from unittest.mock import MagicMock, patch

# 테스트할 대상 파일을 import 합니다.
# VS Code에서 경로 경고가 뜰 수 있지만, pytest는 실행 시 경로를 잘 찾아냅니다.
from ai4pkm_cli.commands.sync_limitless_command import SyncLimitlessCommand

# --- 테스트 시나리오 1: API 키가 없을 때 ---

def test_sync_limitless_when_api_key_is_missing(mocker):
    """
    API 키가 없을 때, 경고 로그를 남기고 조용히 건너뛰는지 테스트합니다.
    """
    # [Arrange / 준비] - 가짜 부품 설정
    
    # 1. os.getenv가 항상 None (값 없음)을 반환하도록 속입니다.
    mocker.patch('os.getenv', return_value=None)
    
    # 2. 가짜 Logger를 만듭니다. 우리는 이 가짜 Logger에 어떤 메시지가 찍히는지 감시할 겁니다.
    mock_logger = MagicMock()

    # [Act / 실행]
    
    # 3. 가짜 Logger를 주입하여 SyncLimitlessCommand 객체를 생성합니다.
    command = SyncLimitlessCommand(logger=mock_logger)
    # 4. 메인 함수를 실행합니다.
    result = command.run_sync()

    # [Assert / 검증]
    
    # 5. 결과가 True인지 확인합니다 (건너뛰는 것은 '성공'으로 간주).
    assert result is True
    
    # 6. "API key not set. Skipping..." 이라는 경고 메시지가 정확히 한 번 호출되었는지 확인합니다.
    mock_logger.warning.assert_called_once_with("LIMITLESS_API_KEY not found in .env file. Skipping sync command.")
    
    # 7. 실제 동기화가 시작되었다는 info 메시지는 절대 호출되지 않았어야 합니다.
    mock_logger.info.assert_not_called()


# --- 테스트 시나리오 2: API 키가 있을 때 ---

# patch 데코레이터를 사용하여 여러 개의 가짜 부품을 한번에 설정합니다.
@patch('ai4pkm_cli.commands.sync_limitless_command.get_localzone')
@patch('ai4pkm_cli.commands.sync_limitless_command.SyncLimitlessCommand.sync_missing_dates')
def test_sync_limitless_when_api_key_exists(mock_sync_missing, mock_get_localzone, mocker):
    """
    API 키가 있을 때, 동기화 프로세스를 정상적으로 실행하는지 테스트합니다.
    """
    # [Arrange / 준비]
    
    # 1. os.getenv가 "fake_api_key" 라는 가짜 키를 반환하도록 속입니다.
    mocker.patch('os.getenv', return_value="fake_api_key")

    # 2. get_localzone (시간대 찾기) 함수가 "Fake/Timezone"을 반환하도록 속입니다.
    mock_get_localzone.return_value = "Fake/Timezone"

    # 3. 가짜 Logger를 만듭니다.
    mock_logger = MagicMock()

    # [Act / 실행]
    
    # 4. SyncLimitlessCommand 객체를 생성하고 메인 함수를 실행합니다.
    command = SyncLimitlessCommand(logger=mock_logger)
    result = command.run_sync()

    # [Assert / 검증]
    
    # 5. 결과가 True (성공)인지 확인합니다.
    assert result is True
    
    # 6. "Starting..." 과 "Using local timezone..." 메시지가 순서대로 호출되었는지 확인합니다.
    mock_logger.info.assert_any_call("Starting Limitless data sync command...")
    mock_logger.info("Using local timezone: Fake/Timezone")
    
    # 7. 가장 중요한 것: 실제 동기화 함수인 sync_missing_dates가 
    #    정확한 타임존 이름과 함께 딱 한 번 호출되었는지 확인합니다.
    mock_sync_missing.assert_called_once_with("Fake/Timezone")