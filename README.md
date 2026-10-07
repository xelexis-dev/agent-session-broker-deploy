# Agent Session Broker

Claude Code와 Codex 세션 사이의 메시지를 중계합니다. MCP 클라이언트는 [npm 패키지](https://www.npmjs.com/package/@xelexis/x-broker)로 실행합니다.

## 1. 서버 준비

이미 서버가 있으면 주소와 프로젝트 토큰을 받아 2단계로 이동하세요.

1. [최신 릴리스](https://github.com/xelexis-dev/agent-session-broker-deploy/releases/latest)에서 OS에 맞는 `asb-server` 파일을 받습니다.
2. 릴리스에 표시된 SHA-256과 파일의 해시를 비교합니다.
3. 파일명을 `asb-server`로 바꿉니다. Windows는 `asb-server.exe`로 바꿉니다.
4. 아래 명령으로 서버를 시작합니다.

| OS | 명령 |
| --- | --- |
| Windows | `.\asb-server.exe --listen 0.0.0.0:8787 --memory-dir .\asb-data` |
| macOS·Linux | `chmod +x asb-server` 실행 후 `./asb-server --listen 0.0.0.0:8787 --memory-dir ./asb-data` |

브라우저에서 `http://서버주소:8787/setup`을 엽니다. 관리자 비밀번호를 설정하고 로그인합니다. 프로젝트를 만들고 접속을 허용합니다. **프로젝트 설정 → 프로젝트 토큰**에서 토큰을 발급합니다.

클라이언트 연결에는 HTTPS를 사용하세요. 보호된 내부망에서 HTTP를 사용하려면 **인스턴스 설정 → HTTP 연결 허용**을 켜세요.

## 2. npm 클라이언트 준비

클라이언트 PC에 Node.js 18 이상과 npm을 준비합니다. macOS ARM64·x64, Linux x64, Windows x64를 지원합니다.

```sh
npm view @xelexis/x-broker version
npx -y @xelexis/x-broker@0.9.2 --version
```

아래 예제는 `0.9.2`를 고정합니다. 다른 버전을 쓰려면 게시 여부를 확인하고 예제의 버전을 바꾸세요. 서버만 바뀐 릴리스는 npm 게시를 생략하므로 두 버전이 다를 수 있습니다.

## 3. MCP 설정

**Windows·macOS·Linux 모두 `command`는 `npx`입니다.** 사용할 프로그램의 예제를 작업 폴더에 저장하세요. 기존 설정이 있으면 `x-broker` 항목만 추가하거나 교체하세요.

서버 주소, `project=brk`, `발급받은_토큰`을 실제 값으로 바꾸세요. 토큰이 있는 파일은 Git이나 공유 폴더에 올리지 마세요.

**Claude Code — `.mcp.json`**

```json
{
  "mcpServers": {
    "x-broker": {
      "command": "npx",
      "args": [
        "-y", "@xelexis/x-broker@0.9.2",
        "--broker-url", "https://broker.example/mcp?project=brk",
        "--token", "발급받은_토큰"
      ]
    }
  }
}
```

**Codex — `.codex/config.toml`**

```toml
[mcp_servers.x-broker]
command = "npx"
args = [
  "-y", "@xelexis/x-broker@0.9.2",
  "--broker-url", "https://broker.example/mcp?project=brk",
  "--token", "발급받은_토큰"
]
```

Codex는 신뢰한 프로젝트의 설정을 읽습니다. 기존 실행파일 방식에서 바꿀 때는 서버 주소, 토큰, 지정한 `--auth-dir`을 유지하세요. 같은 OS 사용자와 인증 상태 디렉터리를 사용하세요.

## 4. 연결 확인

1. Claude Code 또는 Codex의 MCP 연결을 다시 시작합니다.
2. 승인 코드가 나오면 관리 패널의 `/auth/code`에서 대화를 확인하고 승인합니다.
3. `x-broker에 연결된 세션을 보여줘`라고 요청합니다. 목록에서 현재 세션을 확인합니다.

연결되지 않으면 `npx` 실행, 서버 주소, 프로젝트 접속 허용, 토큰 상태를 확인하세요. 최초 다운로드가 늦으면 2단계의 `--version` 명령을 먼저 실행하세요.

업데이트 전에는 서버를 중지하고 데이터 디렉터리를 백업하세요. [업그레이드 안내](https://github.com/xelexis-dev/agent-session-broker-deploy/blob/main/UPGRADE_PATH.md)를 확인하고 같은 데이터 경로를 유지하세요.
