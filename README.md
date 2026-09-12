# Agent Session Broker

Codex와 Claude가 세션 이름으로 메시지를 주고받게 해 주는 프로그램입니다. 대기 중에도 메시지를 자동으로 받아 답할 수 있습니다.

이 저장소는 실행파일 배포용입니다. 아래 안내만으로 설치와 설정을 끝낼 수 있습니다.

## 받을 파일 고르기

[최신 릴리스](https://github.com/xelexis-dev/agent-session-broker-deploy/releases/latest)에서 실행파일을 직접 내려받습니다. 압축 해제나 설치 스크립트가 필요 없습니다.

- 브로커 서버를 돌릴 컴퓨터: `asb-server-<버전>-<OS>-<아키텍처>`
- Claude·Codex를 실행하는 컴퓨터: `asb-client-<버전>-<OS>-<아키텍처>`

| 사용 환경 | 파일명 끝부분 |
| --- | --- |
| Windows x64 | `windows-amd64.exe` |
| Linux x64 | `linux-amd64` |
| Mac Apple Silicon | `darwin-arm64` |
| Mac Intel | `darwin-amd64` |

Linux ARM64용 개별 실행파일은 제공하지 않습니다. Linux ARM64 서버는 아래 Docker 이미지를 사용하세요. 릴리스에 첨부되는 파일은 client와 server 실행파일 8개뿐이며, GitHub가 자동으로 함께 보여 주는 소스 코드 압축은 설치용이 아닙니다.

## 받은 파일 확인하고 실행 준비하기

릴리스 본문의 SHA-256과 받은 파일의 해시를 대조합니다.

| OS | 명령 |
| --- | --- |
| Windows | `Get-FileHash -Algorithm SHA256 <파일>` |
| Linux | `sha256sum <파일>` |
| macOS | `shasum -a 256 <파일>` |

파일명을 `asb-client`와 `asb-server`(Windows는 `.exe`)로 바꾸면 아래 예제를 그대로 사용할 수 있습니다. Linux·macOS에서는 `chmod +x asb-client asb-server`로 받은 파일에 실행 권한을 부여합니다. 받은 구성요소만 지정하면 됩니다.

브라우저에서 내려받은 macOS 파일은 실행 권한을 준 뒤에도 Gatekeeper가 개발자를 확인할 수 없다는 메시지로 실행을 막을 수 있습니다. 해시를 확인한 파일이라면 실행을 한 번 시도한 뒤 **시스템 설정 → 개인정보 보호 및 보안 → 그래도 열기(Open Anyway)**에서 해당 파일을 허용하고 다시 실행합니다. [Apple의 파일별 실행 허용 안내](https://support.apple.com/guide/mac-help/mh40616/mac)를 따르세요. Windows에서도 새로 게시된 실행파일의 평판에 따라 SmartScreen 경고가 표시될 수 있습니다. [Microsoft 안내](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)를 참고하세요.

받은 버전은 `asb-server --version`, `asb-client --version`으로 확인합니다(Windows는 `.exe`). 관리 UI는 서버 실행파일에 포함되어 별도 웹 서버나 Node 설치가 필요 없습니다.

## 서버 구동하기

실행파일을 둔 폴더에서 터미널을 열고 실행합니다.

**Windows**

```powershell
.\asb-server.exe --listen 0.0.0.0:8787 --memory-dir .\asb-data
```

**Linux / macOS**

```bash
./asb-server --listen 0.0.0.0:8787 --memory-dir ./asb-data
```

사용하는 동안 서버를 켜 두세요. 기본 listen 값은 `127.0.0.1:8787`입니다. 다른 PC에서 접속할 때 위처럼 listen 주소를 지정합니다. 인증 토큰과 관리자 비밀번호를 사용하는 연결은 HTTPS 프록시 또는 Tailscale 같은 암호화된 신뢰 네트워크를 사용하세요.

### 최초 설정과 관리 패널

1. `http://서버주소:8787/setup`에서 고정 관리자 `admin`의 비밀번호를 설정합니다. 설정이 저장되면 `/setup`은 다시 사용할 수 없습니다.
2. `/login`에서 로그인하고 프로젝트를 추가합니다. 프로젝트 이름은 소문자 영문·숫자로 시작하며 `.`, `_`, `-`를 포함해 최대 64자입니다.
3. 프로젝트의 **접근 설정**에서 무인증 또는 토큰 인증을 선택합니다. 무인증 프로젝트도 관리자 설정과 프로젝트 생성은 필요합니다.
4. 토큰 인증 프로젝트에서는 **세션 토큰**에 닉네임을 입력해 발급합니다. 원문은 한 번만 표시됩니다. 토큰은 처음 등록한 PC·하네스·대화에 묶이며, 다른 세션에는 별도 토큰을 발급합니다.

무인증 프로젝트는 클라이언트가 요청한 닉네임을 사용합니다. 같은 프로젝트에서 중복이면 UUID 닉네임을 자동 배정하고 등록 결과에 경고합니다. 토큰 인증 프로젝트는 UI에서 지정한 닉네임을 사용하며 클라이언트가 요청한 다른 이름으로 바뀌지 않습니다.

관리 패널에서 프로젝트 접속을 중지하거나 토큰을 취소할 수 있습니다. 변경은 진행 중인 요청과 이후 요청에 적용됩니다. **연결 해제**는 해당 등록을 해제하며 Claude·Codex 프로세스를 종료하지 않습니다. 같은 대화를 서로 다른 PC에서 열면 별도 등록으로 표시됩니다.

### Docker로 서버 구동하기

Linux AMD64와 ARM64 이미지를 제공합니다. Windows·macOS에서는 Linux 컨테이너를 실행하는 Docker 환경을 사용하세요.

빈 폴더에 다음 내용을 `compose.yaml`로 저장합니다.

```yaml
services:
  broker:
    image: ghcr.io/xelexis-dev/agent-session-broker-deploy:latest
    restart: unless-stopped
    ports:
      - "8787:8787"
    volumes:
      - broker-data:/data

volumes:
  broker-data:
```

같은 폴더에서 실행합니다. 최신 버전으로 업데이트할 때도 같은 명령을 사용하세요.

```sh
docker compose pull
docker compose up -d
docker compose ps
```

버전별 이미지는 릴리스가 공개되기 전에 게시와 익명 pull 검증을 마칩니다. `latest`는 릴리스가 확정된 뒤 그 버전으로 옮겨지므로, 특정 버전을 고정하려면 `image`를 `ghcr.io/xelexis-dev/agent-session-broker-deploy:<버전>`으로 지정하세요.

`http://서버주소:8787/healthz`의 `ok`는 서버 실행 확인입니다. 최초에는 `/setup`도 완료해야 연결할 수 있습니다. 로그는 `docker compose logs -f broker`로 확인합니다. 관리자 설정·프로젝트/토큰·등록·공유 메모리는 `broker-data` 볼륨에 보관됩니다. `docker compose down -v`는 이 데이터를 삭제하므로 보관할 때는 `-v`를 붙이지 마세요.

컨테이너는 중앙 서버를 실행합니다. Claude·Codex를 사용하는 각 PC에는 해당 OS의 `asb-client` 실행파일을 준비하고, 아래 설정의 서버 주소를 Docker 서버의 IP 또는 도메인으로 지정하세요. 컨테이너에도 위의 신뢰하는 네트워크 사용 조건이 적용됩니다.

## Claude·Codex 연결하기

사용할 프로그램이 설치된 컴퓨터에 `asb-client` 실행파일을 준비합니다. **작업 폴더**에 해당 프로그램의 설정을 넣으세요. 파일이나 폴더가 없으면 만들고, 기존 설정이 있다면 다른 항목은 유지합니다.

아래 예시에서 `command`는 **Claude·Codex를 실행하는 컴퓨터에 있는 실행파일의 경로**로 바꿉니다. 서버 주소는 다음처럼 지정하세요.

- 서버가 같은 컴퓨터에 있으면 `127.0.0.1`을 그대로 사용합니다.
- 서버가 다른 컴퓨터에 있으면 `127.0.0.1`을 서버의 IP 주소 또는 도메인으로 바꿉니다.

### Claude

`.mcp.json`에 추가합니다.

```json
{
  "mcpServers": {
    "x-broker": {
      "command": "C:/tools/x-broker/asb-client.exe",
      "args": ["--broker-url", "http://127.0.0.1:8787/mcp?project=brk"]
    }
  }
}
```

### Codex

`.codex/config.toml`에 추가합니다.

```toml
[mcp_servers.x-broker]
command = "C:/tools/x-broker/asb-client.exe"
args = ["--broker-url", "http://127.0.0.1:8787/mcp?project=brk"]
```

Linux에서는 `command`를 `/opt/x-broker/asb-client`, macOS에서는 `/Users/사용자명/tools/x-broker/asb-client`처럼 실제 경로로 바꿉니다. JSON에 Windows 경로를 적을 때 `\`는 `\\`로 이스케이프합니다.

`project=brk`의 `brk`는 예시이며 관리 패널에서 만든 프로젝트 이름으로 바꿉니다. 서로 통신할 세션은 같은 서버 주소와 같은 `project` 값을 사용하세요.

토큰 인증 프로젝트에서는 UI에서 받은 토큰을 현재 사용자만 읽을 수 있는 파일에 저장하고 `args`에 `"--token-file", "C:/사용자전용경로/asb-token.txt"`를 추가합니다. 토큰 원문을 URL·MCP 설정 인자·프롬프트에 넣지 않습니다. 파일은 Git에 추가하지 마세요. 무인증 프로젝트는 이 옵션을 생략합니다.

설정을 저장한 뒤 해당 작업 폴더에서 평소처럼 `claude` 또는 `codex`를 실행합니다. 연결 허용 안내가 나오면 확인하세요. 별도 플러그인이나 추가 실행 옵션은 필요 없습니다.

## 사용하기

무인증 프로젝트는 각 세션에 `x-broker에 현재 세션을 'session-1'로 등록해줘.`라고 입력합니다. 다른 세션에는 다른 이름을 지정하세요. 토큰 인증 프로젝트는 해당 토큰에 지정된 UI 닉네임으로 등록됩니다. 실제 배정된 이름은 등록 결과와 세션 목록에서 확인합니다.

등록한 뒤 다음처럼 요청하면 됩니다.

```text
session-2에 "메시지를 받았다면 session-1로 한 번 답장해줘"라고 보내줘.
보낸 뒤 턴을 마치고, 답장이 오면 나에게 보여줘. 추가 답장은 보내지 마.
```

## 재시작과 상태 확인

서버 재시작 후 등록과 닉네임은 보존되며 처음에는 `missing`으로 표시됩니다. 새 클라이언트가 실행 중이면 저장된 소유 증명으로 자동 재접속해 수신 준비를 복구합니다. 서버가 중단된 동안 큐에 있던 메시지는 보존되지 않습니다.

`missing` 등록의 마지막 접촉으로부터 1시간이 지나면 상태 확인을 대기시킵니다. 클라이언트는 제어 응답을 통해 실제 부모 프로세스와 대화를 확인하며 LLM을 호출하지 않습니다. 10분 안에 유효한 응답이 없거나 등록 대상이 달라졌으면 목록에서 제거합니다. 완전히 오프라인인 PC는 복귀 전까지 확인 요청을 받을 수 없습니다. 서버 부팅 직후에는 복구 유예가 적용됩니다.

클라이언트의 PC 식별자와 등록 소유 증명은 사용자 설정 디렉터리의 `agent-session-broker` 폴더에 저장됩니다. `--state-dir` 옵션 또는 `AGENT_SESSION_BROKER_STATE_DIR` 환경변수로 절대 경로를 지정할 수 있습니다. 이 디렉터리를 PC 간 복사하거나 삭제하면 별도 PC 식별·등록 복구에 영향을 줍니다. 명시적으로 해제되거나 만료 정리된 등록은 자동으로 다시 만들지 않습니다.

UUID 닉네임과 대화 ID를 구별해야 하면 `name:<닉네임>`, `session:<대화 UUID>`, `registration:<등록 ID>`를 사용합니다. 같은 대화가 여러 PC에 등록되어 있으면 닉네임 또는 등록 ID로 대상을 선택합니다.

## 예전 버전에서 전환하기

같은 `--memory-dir` 또는 Docker 볼륨을 유지하고 서버와 클라이언트를 모두 업데이트합니다. 최초 `/setup` 후 기존의 정상 프로젝트 디렉터리를 무인증 프로젝트로 가져오며 기존 관리 설정을 덮어쓰지 않습니다. 구버전 서버의 메모리에만 있던 등록은 디스크에 없으므로 최초 전환 때 한 번 등록해야 합니다.

압축본과 설치 스크립트로 설치했던 0.1.11 이하 버전에서 올라오는 경우, `run-broker.sh`와 `run-broker.ps1` 런처는 `.active-version`이 가리키는 `.versions/<버전>/` 안의 실행파일을 사용합니다. **설치 루트에 새 파일을 복사하는 것만으로 이 런처가 새 버전을 선택하지 않습니다.** 다음 순서로 전환하세요.

1. 새 실행파일을 별도 폴더에 두고 `asb-client`/`asb-server`(Windows는 `.exe`)로 이름을 정합니다. 기존 설치 폴더와 데이터는 보관합니다.
2. 서버 시작 명령을 새 `asb-server`의 절대경로로 바꾸고 `--memory-dir`도 기존 데이터의 **절대경로**로 지정합니다. 실행 폴더가 바뀌어도 같은 데이터를 사용해야 합니다.
3. MCP 설정의 `command`를 새 `asb-client` 절대경로로 바꿉니다. 예를 들어 Windows는 `C:\tools\asb\asb-client.exe`, macOS는 `/Users/me/tools/asb/asb-client`, Linux는 `/home/me/tools/asb/asb-client`입니다. 기존 런처를 통하지 않고 직접 실행합니다.
4. 지정한 실행파일에 `--version`을 전달해 새 버전을 확인한 뒤 서버와 MCP 연결을 다시 시작합니다. 디스크 파일 교체만으로 이미 실행 중인 MCP 프로세스가 바뀌지는 않습니다.

클라이언트 옵션 앞에 예전 `client` 서브커맨드를 붙이지 않습니다.

## 연결이 안 될 때

- `http://서버주소:8787/healthz`를 열어 `ok`가 나오는지 확인하세요. 안 나오면 서버 주소, 실행 상태, 방화벽의 8787 포트 허용을 확인합니다.
- 설정을 바꿨다면 Claude·Codex를 다시 열고 이름을 등록하세요.
- 새 클라이언트는 서버 복귀 후 자동 재접속합니다. 등록이 해제·정리됐거나 로컬 소유 증명을 잃었다면 명시적으로 다시 등록해야 합니다.
- `stop_session`으로 등록을 해제했다면 같은 세션에서 다시 등록할 수 있습니다. 무인증 프로젝트에서 이름을 바꾸면 이전 이름은 더 이상 이 세션을 가리키지 않습니다. 토큰 인증 프로젝트에서는 UI에서 지정된 이름을 사용합니다.
- 토큰 거부가 나오면 프로젝트 설정, 토큰 취소 여부, 다른 PC·세션에 이미 묶였는지 확인하세요. 중복 MCP 클라이언트가 같은 등록을 점유하고 있으면 중복 설정을 정리한 뒤 연결합니다.
- 문제가 계속되면 각 PC의 클라이언트를 [최신 릴리스](https://github.com/xelexis-dev/agent-session-broker-deploy/releases/latest)의 파일로 교체하고 MCP 연결을 다시 시작한 뒤 등록하세요.
- `x-broker에 연결된 세션을 보여줘`라고 요청해 상대가 등록되어 있는지 확인하세요.

메시지를 받으려면 서버와 상대 세션이 켜져 있어야 합니다. 송신 성공은 브로커의 큐 접수를 뜻하며 상대 모델이 읽었다는 확인은 아닙니다. 연결 복구 시 실패한 송신을 자동 재전송하지 않습니다. 응답이 끊기기 전에 이미 접수됐을 수 있으므로 다시 보내기 전에 상대의 수신 여부를 확인하세요.

작업 중에는 답장이 늦어질 수 있고, 연결 만료·수신 실패·서버 재시작 시 미전달 메시지는 사라질 수 있으므로 중요한 요청은 답장까지 확인하세요.
