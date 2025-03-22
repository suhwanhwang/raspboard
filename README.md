# Weather Frame for Raspberry Pi

라즈베리 파이용 날씨 디지털 액자 프로그램입니다.

## 기능
- 현재 시간과 날짜 표시
- 현재 날씨 정보 표시 (온도, 날씨 상태, 아이콘)
- 5분마다 날씨 정보 자동 업데이트
- 일주일 날씨 예보 표시
- 전체 화면 모드 지원

## 설치 방법

1. 프로젝트 클론:
```bash
git clone [repository-url]
cd raspboard
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

4. 한글 폰트 설치:
```bash
sudo apt-get update
sudo apt-get install fonts-nanum
```

5. OpenWeatherMap API 키 발급:
- [OpenWeatherMap](https://openweathermap.org/) 웹사이트에서 회원가입
- API 키 발급 받기

6. 환경 변수 설정:
- `.env` 파일 생성
```bash
cp .env.example .env
```
- `.env` 파일에서 `OPENWEATHER_API_KEY`에 발급받은 API 키 입력
- `CITY` 값을 원하는 도시로 변경 (기본값: Seoul)

## 수동 실행 방법

가상환경이 활성화된 상태에서:
```bash
python weather_frame.py
```

또는 실행 스크립트 사용:
```bash
./start_weather.sh
```

## 자동 시작 설정

1. 실행 스크립트 권한 설정:
```bash
chmod +x start_weather.sh
```

2. 자동 시작 디렉토리 생성 및 데스크톱 엔트리 복사:
```bash
mkdir -p ~/.config/autostart
cp weather-frame.desktop ~/.config/autostart/
```

3. 경로 설정:
- `start_weather.sh`와 `weather-frame.desktop` 파일에서 프로젝트 경로를 실제 설치 경로로 수정
  - 기본값은 `/home/pi/raspboard`로 설정되어 있음
  - 다른 경로에 설치한 경우 해당 파일들의 경로를 수정해야 함

## 프로그램 종료
- ESC 키를 누르면 프로그램이 종료됩니다.

## 주의사항
- 프로그램 실행을 위해서는 인터넷 연결이 필요합니다.
- 화면 끄기를 방지하려면 라즈베리 파이의 전원 관리 설정을 조정해야 합니다.
- 날씨 정보는 5분마다 자동으로 업데이트됩니다.

## 문제 해결
- 한글이 표시되지 않는 경우: 나눔 폰트가 설치되어 있는지 확인
- 날씨 정보가 표시되지 않는 경우: API 키와 인터넷 연결 확인
- 자동 실행이 되지 않는 경우: 경로 설정과 실행 권한 확인 