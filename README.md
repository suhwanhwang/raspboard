# Weather Frame for Raspberry Pi

라즈베리 파이용 날씨 디지털 액자 프로그램입니다.

## 기능
- 현재 시간과 날짜 표시
- 현재 날씨 정보 표시 (온도, 날씨 상태, 아이콘)
- 5분마다 날씨 정보 자동 업데이트
- 전체 화면 모드 지원

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. OpenWeatherMap API 키 발급:
- [OpenWeatherMap](https://openweathermap.org/) 웹사이트에서 회원가입
- API 키 발급 받기

3. 환경 변수 설정:
- `.env` 파일에서 `OPENWEATHER_API_KEY`에 발급받은 API 키 입력
- `CITY` 값을 원하는 도시로 변경 (기본값: Seoul)

## 실행 방법

```bash
python weather_frame.py
```

## 자동 시작 설정 (라즈베리 파이)

1. 자동 시작 스크립트 생성:
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/weather-frame.desktop
```

2. 다음 내용 입력:
```
[Desktop Entry]
Type=Application
Name=Weather Frame
Exec=python /path/to/weather_frame.py
```

## 주의사항
- 프로그램 실행을 위해서는 인터넷 연결이 필요합니다.
- 화면 끄기를 방지하려면 라즈베리 파이의 전원 관리 설정을 조정해야 합니다. 