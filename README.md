# Agent Session Broker

ASB는 Claude Code·Codex·Kimi 대화 사이의 메시지를 중계하는 도구입니다. 서버가 프로젝트·접속 권한·등록을 관리하고, 각 PC의 MCP 클라이언트가 사용자가 연 대화에 연결됩니다.

**에이전트 설정과 상세 운용 절차는 [README_AGENT.md](README_AGENT.md)를 읽으세요.** MCP 설정, Codex 재개·hook, 여러 프로젝트, 관리 API 명세, 오류·버그 리포트·재연결 안내를 담고 있습니다.

## 서버 설치와 실행

Docker Compose를 사용할 수 있는 서버에 아래 내용을 `compose.yaml`로 저장합니다. `./data`는 서버 데이터 경로이므로 영속 보관하고 백업하세요. 포트는 이 서버(127.0.0.1)에만 엽니다. 다른 PC 연결은 아래 3단계를 따르세요.

```yaml
services:
  broker:
    image: ghcr.io/xelexis-dev/agent-session-broker-deploy:0.20.2
    restart: unless-stopped
    ports:
      - "127.0.0.1:8787:8787"
    volumes:
      - ./data:/data
```

```sh
docker compose up -d
```

1. **설정 코드 확인**: 0.20.2은 최초 관리자 설정에 데이터 폴더의 일회용 코드가 필요합니다. 서버에서 `docker compose exec broker cat /data/control/setup-code`로 확인합니다. 최초 설정 전에는 외부에 포트를 열지 마세요.
2. **관리자 설정**: 서버에서 `http://127.0.0.1:8787/setup`을 엽니다. 원격 서버는 `ssh -L 8787:127.0.0.1:8787 <서버>` 뒤 같은 주소를 씁니다. 확인한 설정 코드와 새 관리자 비밀번호를 입력하고 로그인합니다.
3. **다른 PC에서 연결**: 외부 연결에는 HTTPS를 사용하세요. TLS proxy 뒤라면 서버의 `--trusted-proxy`와 원래 scheme 전달 설정이 필요합니다. **인스턴스 설정 → HTTP 연결 허용**이 OFF이면 평문 MCP·관리 API 연결은 localhost도 거부됩니다. HTTP를 허용하면 토큰·비밀번호가 통신 경로에 노출될 수 있습니다. 보호된 내부망에서 직접 HTTP를 사용할 때만 포트를 `"8787:8787"`로 바꾸고 **인스턴스 설정 → HTTP 연결 허용**을 켭니다. 평문 연결은 비밀번호와 토큰을 노출할 수 있습니다.

**0.20.2의 설정 코드**: `docker compose exec broker cat /data/control/setup-code`로 파일을 읽고 코드와 관리자 비밀번호를 함께 입력해야 합니다. 파일이 없거나 읽기 실패면 먼저 서버 시작 상태와 데이터 경로를 확인하세요. 코드를 생략하는 우회는 없습니다. 코드는 재시작하면 바뀌고 설정 성공 후 지워지며 로그에는 파일 위치만 나옵니다. 코드·설정 전 백업을 비밀로 보관하세요.

이미 설정했다면 같은 서버 주소의 관리 패널을 사용합니다. 실행파일 설치는 [최신 릴리스](https://github.com/xelexis-dev/agent-session-broker-deploy/releases/latest)를 확인하세요.

## 클라이언트 설치와 대화 연결

각 PC에 Node.js 22 이상과 npm을 준비합니다. 클라이언트는 [npm 패키지](https://www.npmjs.com/package/@xelexis/x-broker)로 설치합니다.

```sh
npm view @xelexis/x-broker version
npm install -g @xelexis/x-broker@0.20.2
x-broker --version
```

서버만 바뀐 릴리스는 npm 게시를 생략할 수 있으므로 게시된 버전과 권장 버전을 확인하세요. 전역 설치는 사용자가 직접 수행합니다.

1. 관리 패널에서 프로젝트를 만들고 접속을 허용한 뒤 **프로젝트 설정 → 프로젝트 토큰**에서 PC별 토큰을 발급합니다.
2. Claude Code·Codex·Kimi의 MCP 설정에 `x-broker`를 추가하고 서버 주소·프로젝트·토큰을 지정합니다. [하네스별 설정 예제](README_AGENT.md#3-mcp-설정)를 따르세요. 자격증명이 들어 있는 설정은 Git이나 공유 폴더에 올리지 마세요.
3. MCP를 재연결하고 대화에서 **“이 대화를 x-broker에 연결해 줘”**라고 요청합니다. 승인 코드가 나오면 관리 패널의 승인 화면에서 대화를 확인합니다. 새 대화를 여는 것만으로 등록되지는 않습니다.

## 일상 운용과 업데이트

관리 패널에서 프로젝트·멤버·토큰과 연결된 세션을 확인합니다. 토큰은 필요한 권한과 수명만 주고, 유출되거나 더 이상 필요하지 않으면 취소하세요.

자동화용 **관리 API**는 MCP와 별도이며 기본 OFF입니다. 관리자가 인스턴스 설정의 관리 API 스위치를 켜야 합니다. 내 프로필에서 자기 API 토큰을 등록·조회·취소할 수 있고, 관리자는 사용자 상세에서 토큰을 조회·취소합니다. [에이전트용 관리 API 안내](README_AGENT.md#관리-api)에 scope·재인증·안전한 호출 예제가 있습니다.

0.20.2은 1.0 릴리스 후보입니다. **모든 PC의 클라이언트 먼저 갱신 → 서버 중지와 전체 데이터 백업 → 서버 교체 → MCP 재연결과 실제 연결 확인** 순서로 업데이트하세요. 0.17.3 미만 client와 legacy 연결은 거부됩니다. Compose 사용자는 image 버전을 바꾼 뒤 `docker compose pull`과 `docker compose up -d`로 교체합니다. 운영 데이터 경로를 유지하고, 롤백은 전체 백업과 이전 버전을 함께 복원하세요.

버전별 변경과 주의 사항은 [UPDATE.md](https://github.com/xelexis-dev/agent-session-broker-deploy/blob/main/UPDATE.md), [업그레이드 경로](https://github.com/xelexis-dev/agent-session-broker-deploy/blob/main/UPGRADE_PATH.md), [연결된 채 갱신하기](README_AGENT.md#연결된-채-업그레이드)를 확인하세요. 관리 API 토큰 유출 대응으로 다운그레이드할 때는 먼저 토큰을 취소해야 합니다.

## 라이선스

이 소프트웨어는 MIT 라이선스로 제공됩니다. 자세한 조건은 [LICENSE](LICENSE), 제3자 구성요소의 라이선스와 고지는 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)를 확인하세요.
