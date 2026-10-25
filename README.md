# Agent Session Broker

Claude Code와 Codex 세션 사이의 메시지를 중계합니다. MCP 클라이언트는 [npm 패키지](https://www.npmjs.com/package/@xelexis/x-broker)로 실행합니다.

## 1. 서버 준비

이미 서버가 있으면 주소와 프로젝트 토큰을 받아 2단계로 이동하세요.

버전별 변경 사항은 [UPDATE.md](https://github.com/xelexis-dev/agent-session-broker-deploy/blob/main/UPDATE.md)에서 확인하세요.

1. [최신 릴리스](https://github.com/xelexis-dev/agent-session-broker-deploy/releases/latest)에서 OS에 맞는 `asb-server` 파일을 받습니다.
2. 릴리스에 표시된 SHA-256과 파일의 해시를 비교합니다.
3. 파일명을 `asb-server`로 바꿉니다. Windows는 `asb-server.exe`로 바꿉니다.
4. 아래 명령으로 서버를 시작합니다.

| OS | 명령 |
| --- | --- |
| Windows | `.\asb-server.exe --listen 0.0.0.0:8787 --memory-dir .\asb-data` |
| macOS·Linux | `chmod +x asb-server` 실행 후 `./asb-server --listen 0.0.0.0:8787 --memory-dir ./asb-data` |

브라우저에서 `http://서버주소:8787/setup`을 엽니다. 관리자 비밀번호를 설정하고 로그인합니다. 프로젝트를 만들고 접속을 허용합니다. **프로젝트 설정 → 프로젝트 토큰**에서 토큰을 발급합니다.

토큰은 PC마다 하나씩 발급하고 닉네임에 PC 이름을 적으세요. PC별 등록을 추적하고 폐기 대상을 구분하기 쉽습니다. 사람이 사용하는 PC에는 승인 필요한 토큰을 우선하세요. 코드와 닉네임이 채워진 승인 링크에서 대화를 확인하고 한 번 승인하면 됩니다. 무승인 토큰은 무인 실행에 사용하고 세션 상한과 유효기간을 함께 설정하세요.

연결 요청 시 승인 없이 등록하는 토큰은 발급할 때 등록 한도와 수명을 선택합니다. 기본값은 8개·30일이며, 한도는 1~100000개 또는 **무제한**, 수명은 1~36500일 또는 **무기한**으로 지정할 수 있습니다(서버 0.17.0부터). 프로젝트 전체 등록 한도와 요청 제한은 그대로 적용됩니다. 무제한 또는 이전 범위(64개·90일)를 넘는 토큰을 발급한 뒤 서버를 0.16 이하로 내리려면 업그레이드 전 데이터 백업을 복원해야 합니다.

클라이언트 연결에는 HTTPS를 사용하세요. 보호된 내부망에서 HTTP를 사용하려면 **인스턴스 설정 → HTTP 연결 허용**을 켜세요.

## 2. npm 클라이언트 준비

클라이언트는 Windows·macOS·Linux 모두 npm/npx로 배포합니다. GitHub Release는 서버 실행파일 4개를 제공합니다.

클라이언트 PC에 Node.js 18 이상과 npm을 준비합니다. macOS ARM64·x64, Linux x64, Windows x64를 지원합니다.

대화별 클라이언트 상태는 30일 동안 사용하지 않으면 자동 삭제하며, 진단 기록은 14일 후 정리합니다.

```sh
npm view @xelexis/x-broker version
npx -y @xelexis/x-broker@0.17.2 --version
```

아래 예제는 `0.17.2`를 고정합니다. 다른 버전을 쓰려면 게시 여부를 확인하고 예제의 버전을 바꾸세요. 서버만 바뀐 릴리스는 npm 게시를 생략하므로 두 버전이 다를 수 있습니다.

`@latest`는 MCP 프로세스를 시작하기 전에 npm 레지스트리 확인과 다운로드로 지연될 수 있습니다. MCP 연결에는 예제처럼 게시된 버전을 고정하고, 같은 버전의 `--version`을 먼저 실행해 준비하세요. `--version`은 버전 확인이며 대화 연결 검사가 아닙니다. 하네스 밖에서 인자 없이 실행한 결과로 부모 대화 연결 여부를 판단하지 마세요.

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
        "-y", "@xelexis/x-broker@0.17.2",
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
  "-y", "@xelexis/x-broker@0.17.2",
  "--broker-url", "https://broker.example/mcp?project=brk",
  "--token", "발급받은_토큰"
]
```

클라이언트 0.17.1에서 `--nickname 이름`으로 연결 시 요청할 통신 이름을 지정할 수 있습니다. 서버가 직접 등록을 지원하고 토큰이 승인 없는 등록을 허용할 때 사용합니다. 이름이 겹치면 대체 이름을 받을 수 있으므로 `auth_status`의 최종 이름을 확인하세요. 직접 등록을 지원하지 않는 서버는 기존 수동 승인 흐름을 사용합니다. 제한 권한·자동 등록 토큰 발급은 인스턴스 관리자가 설정을 켜야 하며 기본값은 꺼짐입니다.

Codex는 신뢰한 프로젝트의 설정을 읽습니다. 기존 실행파일 방식에서 바꿀 때는 서버 주소, 토큰, 지정한 `--auth-dir`을 유지하세요. 같은 OS 사용자와 인증 상태 디렉터리를 사용하세요.

### Codex 수명 주기 hook

아래 `.codex/hooks.json` 예제의 `turn_id`는 **클라이언트 0.17.2 이상에서만** 전달하세요. 기존 0.17.1 client의 hook 입력 스키마는 정의되지 않은 키를 거절합니다. client를 먼저 0.17.2 이상으로 업그레이드하고 MCP를 재시작한 뒤 설정을 바꾸세요.

```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "mcp_tool", "server": "x-broker", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10}]}],
    "PreToolUse": [{"matcher": "*", "hooks": [{"type": "mcp_tool", "server": "x-broker", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10}]}],
    "PostToolUse": [{"matcher": "*", "hooks": [{"type": "mcp_tool", "server": "x-broker", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10}]}],
    "Stop": [{"hooks": [{"type": "mcp_tool", "server": "x-broker", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10}]}],
    "Interrupt": [{"hooks": [{"type": "mcp_tool", "server": "x-broker", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}"}, "timeout": 10}]}]
  }
}
```

Codex 0.164.0의 실제 hook과 rollout에서 같은 턴 ID가 전달됨을 확인했습니다. 새 client는 `turn_id`가 없는 기존 설정도 받아 기존 도구 경계·Stop 전달을 유지합니다. 다만 ID가 없거나, 제한된 rollout 끝부분에서 해당 턴의 마지막 시작과 종료 쌍을 검증하지 못하면 Stop 누락 자동 배출은 하지 않고 다음 hook까지 pending을 유지합니다. 시간 경과나 화면의 idle 표시만으로 턴 종료를 추정하지 않습니다.

### Kimi Code (macOS·Linux, turn-boundary 수신)

Kimi는 프로젝트 루트의 `.mcp.json`을 읽습니다. 위 Claude 예제와 같은 형식을 쓰되 **서버와 클라이언트 모두 0.17.2 이상**이 필요합니다. 이전 서버에 연결하면 등록을 시도하기 전에 `unsupported-server`로 안내합니다. Windows Kimi는 지원하지 않습니다.

Kimi 홈 `~/.kimi-code/config.toml`(또는 `$KIMI_CODE_HOME/config.toml`)에 아래 hook을 설정하세요. 자동으로 전역 설정을 바꾸지 않습니다. hook 명령에 broker 토큰을 넣지 마세요.

MCP 설정과 같은 고정 버전을 `npm install -g @xelexis/x-broker@0.17.2`로 설치하고, `command -v x-broker`가 출력한 절대 경로를 아래 hook 명령에 사용하세요. hook의 `PATH`에서 `node`를 찾을 수 있어야 하며, 업그레이드할 때도 전역 설치 버전을 MCP 설정과 같게 유지하세요.

```toml
[[hooks]]
event = "SessionStart"
command = '"/absolute/path/x-broker" kimi-hook --auth-dir "/absolute/path/client-state"'
timeout = 5

[[hooks]]
event = "UserPromptSubmit"
command = '"/absolute/path/x-broker" kimi-hook --auth-dir "/absolute/path/client-state"'
timeout = 5

[[hooks]]
event = "Stop"
command = '"/absolute/path/x-broker" kimi-hook --auth-dir "/absolute/path/client-state"'
timeout = 5
```

MCP client의 `--auth-dir`/`--state-dir`와 hook의 경로를 같게 지정하세요. 둘 다 생략하면 동일한 `AGENT_SESSION_BROKER_STATE_DIR` 환경변수와 사용자 기본 경로를 사용합니다. 경로가 다르면 hook이 소켓을 찾지 못해 `kimi-session-unknown`이 됩니다. 긴 상태 경로는 소유권을 확인한 짧은 사용자 전용 디렉터리로 소켓만 옮깁니다. 소켓 bind 실패는 `auth_status`에 `kimi-hook-unavailable`로 표시됩니다.

메시지는 **다음 eligible UserPromptSubmit 또는 Stop hook**에서 전달합니다. idle·실패·이미 Stop으로 이어진 턴은 다음 사용자 입력까지 기다릴 수 있습니다. idle 대화를 깨우지 않습니다. `auth_status`의 `delivery: "turn-boundary"`와 `pendingMessages`를 확인하세요. 공개 세션 목록의 `automaticDeliveryReady: false`는 이 제한을 뜻하며, 큐 접수를 막지 않습니다. 활동은 `unknown / unsupported`입니다.

Kimi 2.3.1은 한 턴의 Stop continuation을 한 번만 실행합니다. 그 뒤 도착한 메시지는 다음 사용자 입력까지 남습니다. client가 batch를 hook으로 넘긴 뒤 Esc·timeout 등으로 hook이 중단되면 그 batch가 유실될 수 있으며, `kimi-hook-handoff` 진단은 handoff만 기록하고 모델 수신을 증명하지 않습니다. 대화가 바뀌면 기존 수신을 차단하고 `reconnect-required`를 표시합니다. 새 대화로 MCP를 재연결한 뒤 명시적으로 연결을 요청하세요.

## 4. 연결 확인

1. Claude Code 또는 Codex의 MCP 연결을 다시 시작합니다.
2. `이 대화를 x-broker에 연결해 줘`라고 요청합니다.
3. 승인 코드가 나오면 관리 패널의 `/auth/code`에서 대화를 확인하고 승인합니다. `session:register:auto` 권한이 있는 토큰은 이 연결 요청 시 승인 절차 없이 등록합니다.
4. `auth_status`로 등록 상태와 최종 이름을 확인하고, `x-broker에 연결된 세션을 보여줘`라고 요청해 목록에서 현재 세션을 확인합니다.

이 연결 요청 방식은 클라이언트 0.17.1부터 적용됩니다. 새 대화가 시작되는 것만으로 등록하지 않습니다. 0.17.0 이하 client는 시작 시 자동 등록을 시도하는 기존 동작을 유지합니다.

연결되지 않으면 `npx` 실행, 서버 주소, 프로젝트 접속 허용, 토큰 상태를 확인하세요. 최초 다운로드가 늦으면 2단계의 `--version` 명령을 먼저 실행하세요.

업데이트 전에는 서버를 중지하고 데이터 디렉터리를 백업하세요. [업그레이드 안내](https://github.com/xelexis-dev/agent-session-broker-deploy/blob/main/UPGRADE_PATH.md)를 확인하고 같은 데이터 경로를 유지하세요.

### 대화를 재개해도 연결 유지

클라이언트 0.17.1은 `claude --resume` 또는 새로 시작한 Claude 안에서 `/resume`으로 대화를 재개하면 `/mcp` 조작 없이 같은 등록과 이름을 이어 씁니다.

- 서버도 0.17.1이면 `/clear` 뒤 새 대화로 등록을 인계합니다. `/resume`으로 원래 대화에 돌아오면 등록을 다시 가져옵니다.
- `claude --bg`로 실행한 백그라운드 세션, `/resume`으로 붙은 뷰어, `claude stop` 후 `claude --resume`도 연결을 이어 갑니다.
- 구서버에서는 `/clear` 뒤 등록을 인계하지 않습니다. 그동안 도착한 메시지는 보류하고 원래 대화로 `/resume`한 뒤 전달합니다. 원래 대화로 돌아오기 전에 Claude를 종료하면 보류한 메시지는 전달되지 않습니다.

수동 승인 토큰(자동 등록 권한 없음)은 `/clear`나 대화 전환 뒤 자동으로 인계하지 않습니다. 새 대화에서 사용자가 연결을 요청하면 승인 링크가 나오고, 승인하면 기존 등록의 이름, 등록 ID, 대기 메시지를 이어받습니다. 승인 화면에는 임시 이름(`<이름>-next`)이 보이며 승인 뒤 원래 이름으로 바뀝니다. 서버와 클라이언트 모두 0.17.1이 필요합니다. 설정 파일에 고정한 세션 자격은 인계를 지원하지 않습니다.

### 무응답 세션 등록

오래 통신하지 않은 세션도 등록 목록에 `missing`(응답 없음)으로 남습니다. 상태 확인 probe가 무응답이거나 식별 확인에 실패해도 자동 삭제하지 않습니다. 같은 세션이 재연결하면 기존 등록 ID와 이름을 이어 씁니다. 세션 자격증명이 만료되면 재승인 후 연결할 수 있으며 등록 행은 유지됩니다. 관리 화면에서 등록을 해제하면 이름이 바로 풀립니다. `stop_session`으로 연결을 해제하면 해제된 기록이 약 1시간 10분 동안 이름을 유지한 뒤 사라집니다. 명시적 재등록 교체·프로젝트 삭제도 등록을 제거할 수 있습니다. 등록 상한(1,024개)에 도달하면 새 등록을 거부하므로 관리자에게 오래된 세션의 연결 해제를 요청하세요.

### heartbeat 진단 확인

`auth_status` 응답의 `diagnostics`에서 마지막 lease 갱신 성공 시각(`lastRenewSuccess`), 마지막 실패 시각·종류·사유 코드·오류 분류(`lastFailureAt`, `lastFailureReason`, `lastFailureCode`, `lastFailureClass`), receiver 종료 사유와 인증 상태를 확인할 수 있습니다. 시각은 UTC입니다. 진단 기록 조회는 로컬에서 읽으며, 토큰 권한 조회는 아래 설명대로 서버에 요청할 수 있습니다. 복구되어도 마지막 실패 기록은 남으므로 성공·실패 시각을 함께 비교하세요. 기록을 읽을 수 없으면 `unavailable: true`가 표시됩니다.

### 토큰 권한 확인

`auth_status`의 `scopes`는 현재 세션 자격증명의 권한이고, `scopeDetails`는 각 권한의 라벨과 설명입니다. `scopeSource`가 `server`이면 서버의 현재 자격증명 정보, `stored`이면 구 서버 또는 조회 실패 시 로컬 저장 정보, `unknown`이면 확인할 정보가 없습니다. `admissionMode`와 `credentialExpiresAt`은 확인 가능한 경우 함께 표시합니다. 승인을 기다리는 코드의 `expiresAt`과 자격증명 만료는 별개입니다.

서버와 클라이언트 0.17.1부터 서버의 현재 권한을 조회합니다. 지원 서버에는 호출당 최대 한 번 읽기 전용 조회를 하고 요청 context에 2초 제한을 적용하며, 실패해도 `auth_status`는 성공합니다. 진단 기록은 계속 로컬에서 읽습니다. 권한이 있어도 별도의 세션 신원·소유권 검사는 그대로 적용됩니다.

| scope | 라벨 | 설명 |
| --- | --- | --- |
| `memory:read` | 메모리 조회 | memory_get과 memory_search로 프로젝트 메모리를 조회합니다. |
| `memory:write` | 메모리 쓰기 | memory_put으로 프로젝트 메모리를 저장합니다. |
| `message:receive` | 메시지 수신 | wait_for_message로 자기 세션에 도착한 메시지를 수신합니다. |
| `message:send` | 메시지 발송 | send_message로 등록된 자기 세션에서 다른 세션으로 메시지를 보냅니다. |
| `session:manage` | 세션 관리 | stop_session으로 이 세션의 연결을 해제하며, stop_session·suspend_session·unsuspend_session으로 토큰 소유자가 관리할 수 있는 다른 세션의 연결을 해제·일시 중지·재개합니다. 이 세션의 일시 중지·재개는 허용되지 않습니다. |
| `session:read` | 세션 조회 | list_sessions와 get_session으로 프로젝트 세션을 조회합니다. |
| `session:register` | 등록·연결 유지 (필수) | attach_session·register_session·resume_session·renew_lease·probe_response·report_ingress_failure로 자기 세션을 등록하고 연결을 유지합니다. |
| `session:register:auto` | 연결 요청 시 승인 없이 등록 | 사용자가 이 대화의 연결을 요청하면 승인 절차 없이 등록합니다. 새 대화가 시작되는 것만으로 등록하지 않습니다. 프로젝트 토큰으로 사람의 승인 없이 직접 등록을 요청하며 세션 자격증명에는 위임되지 않습니다. |
| `session:rename` | 자기 이름 변경 | rename_session으로 자기 세션의 통신 이름을 변경합니다. |
| `session:spawn` | 세션 생성 | spawn_session 호출 권한이며 현재 원격 서버는 프로세스를 시작하지 않고 지원하지 않는다는 안내를 반환합니다. |

전체 기록은 client 인증 상태 디렉터리(`--auth-dir`) 아래 `diagnostics/<binding-key>.json`에 대화별로 저장됩니다. 프로젝트 토큰 방식의 `auth_status`가 없는 기존 연결 방식에서는 이 파일을 확인하세요. 파일은 최근 256건·최대 128 KiB를 유지하며 갱신 성공은 요약 시각만 갱신합니다. 파일 권한은 기존 상태 파일과 같은 0600입니다. 기록에는 세션·등록 ID, generation, 시각과 고정된 사유·분류·인증 상태만 담고 토큰·URL·실행 인자·메시지 본문·오류 원문은 저장하지 않습니다. 기록 저장 실패는 연결을 중단하지 않으며 강제 종료 순간의 종료 사유는 기록되지 않을 수 있습니다.

### 세션 관리 권한

서버 0.17.1부터 `session:manage`로 이 세션의 연결을 해제하고, 토큰 소유자가 관리할 수 있는 다른 세션의 연결 해제·일시 중지·재개를 요청할 수 있습니다. 서버 업데이트 후에는 이 권한을 가진 기존 토큰에도 같은 규칙이 적용됩니다.

- Owner 토큰은 같은 프로젝트의 모든 세션을 관리합니다. Developer 토큰은 같은 소유자의 세션만 관리합니다.
- 이 세션 자신은 `stop_session`으로 연결 해제만 할 수 있습니다. 자신의 `suspend_session`·`unsuspend_session` 호출은 허용되지 않습니다. 소유자 정보가 없는 기존 토큰도 자기 연결 해제만 할 수 있습니다.
- `stop_session`은 대상 프로세스를 종료하지 않고 연결을 해제하며 대기 메시지를 비웁니다. 이름은 약 1시간 10분 유지되며, 관리 화면에서 해제하면 바로 풀립니다. 대상 대화의 사용자가 다시 연결을 요청할 때만 등록됩니다.
- `suspend_session`은 관리할 수 있는 다른 세션의 연결을 일시 중지하고 대기 메시지를 버리며 진행 중 요청을 취소합니다. `unsuspend_session`은 그 세션을 재개하며 대상은 다음 lease부터 다시 연결됩니다.
- 다른 프로젝트의 세션은 관리할 수 없습니다. 권한은 매 호출 시 현재 역할·소유권·토큰 상태로 다시 확인하므로 역할 강등·멤버 제외·토큰 회수도 반영됩니다.

`suspend_session`·`unsuspend_session`은 클라이언트 0.17.1에서 도구 목록에 표시됩니다. 실행 중인 0.17.0 클라이언트는 기존 도구 목록을 유지합니다. 기존 `stop_session`으로 다른 세션을 해제하는 기능은 서버만 0.17.1로 올려도 권한 범위 안에서 사용할 수 있습니다.

관리 화면의 **세션 감사**에서 관련 이력을 확인할 수 있습니다. 감사 화면의 활성화 조건은 기존과 같습니다.

### 메시지 전달 시각

수신 메시지의 envelope는 `from`, `to`, `body`와, 수신 client가 `message.sentAt` 지원을 선언한 경우 broker가 수락한 시각 `sentAt`(RFC 3339 UTC, 밀리초 정밀도)을 담습니다. `from`은 신뢰할 수 없는 표시 이름이며 송신자가 제공한 시각도 신뢰하지 않습니다. broker가 시각을 정하고, 전달 대기 중에도 그 시각을 유지합니다. 원격 envelope의 12,000-byte 한도는 `sentAt`과 broker의 라우팅 필드를 포함합니다.

메시지 시각은 서버와 클라이언트 0.17.0부터 지원합니다. 구서버는 `sentAt`을 생략하고 구 client에는 기존 envelope 모양을 유지합니다. 새 client는 서버의 지원 선언이 있는 연결에서만 등록 capability를 전송하므로 구서버의 엄격한 입력 스키마도 유지됩니다. 구 client의 엄격한 MCP 결과 스키마를 유지하기 위해 `send_message` 응답 필드는 바꾸지 않습니다.

## 버그 리포트

에이전트는 x-broker 도구가 설명과 다르게 동작하거나 실패하면 `report_bug`로 관리자에게 보고할 수 있습니다. 서버와 클라이언트 모두 0.17.1이 필요합니다.

- 클라이언트는 버전, OS, 인증·수신 상태와 최근 진단 이벤트 최대 20개를 붙입니다. 자동 진단에는 토큰, 파일 경로, 메시지 본문을 넣지 않습니다. 보고 내용에도 비밀값을 넣지 마세요. 서버는 x-broker 토큰 형식의 문자열을 한 번 더 가립니다.
- 등록당 시간당 10건, 프로젝트당 하루 200건까지 받습니다. 제한에 걸리면 재시도 시각을 안내합니다.
- 관리자는 **관리자 전용 → 버그 리포트**에서 내용을 확인하고 닫거나 다시 열 수 있습니다.
- 인스턴스에 최대 2,000건을 180일까지 보관합니다. 개수나 기간을 넘으면 오래된 것부터 지웁니다. 프로젝트를 삭제하면 해당 리포트도 삭제합니다.

## 버전 호환

| 조합 | 사용할 수 있는 기능 |
| --- | --- |
| 서버 0.17.2 + 클라이언트 0.17.1 | 기존 연결·메시지와 서버의 프로젝트 기록 격리·관리 화면을 지원합니다. 새 도구 입력과 프로젝트 종료 안내·수신 프로세스 보호에는 클라이언트도 0.17.2가 필요합니다. |
| 클라이언트 0.17.2 + 서버 0.17.1 | 기존 연결·메시지를 지원합니다. 프로젝트 종료 판단·수신 프로세스 보호는 지원하지 않습니다. `expectRegistrationId`는 `unsupported`, Kimi 연결은 `unsupported-server`로 거부합니다. |

업데이트 순서는 **전체 인스턴스 데이터 백업 → 서버 0.17.2 → npm 클라이언트 0.17.2 → 각 대화 재연결**입니다.

1. 서버를 중지하고 전체 데이터 디렉터리를 백업합니다. 기존 클라이언트 상태도 보존합니다.
2. 같은 데이터 경로로 서버 0.17.2를 시작합니다. 첫 시작에 프로젝트 세대 ID를 부여하고 `controlVersion`을 5로 올립니다.
3. MCP 설정의 npm 버전을 `@xelexis/x-broker@0.17.2`로 바꾸고 `npx -y @xelexis/x-broker@0.17.2 --version`으로 준비합니다.
4. 각 Claude 대화에서 `/mcp`로 재연결하거나 Claude를 재시작합니다. Codex도 각 세션의 앱·프로세스를 재시작하고, Kimi도 MCP를 재연결해 새 클라이언트를 적용합니다.

롤백할 때는 서버를 중지하고 **업그레이드 전 전체 데이터 백업과 이전 실행파일을 함께 복원**합니다. `control.db`만 되돌리지 마세요. 자세한 혼합 버전 제한과 복원 조건은 [업그레이드 안내](https://github.com/xelexis-dev/agent-session-broker-deploy/blob/main/UPGRADE_PATH.md)를 확인하세요.

서버 버전별로 지원하는 클라이언트 최소 버전을 관리합니다. `client-incompatible` 또는 `server-incompatible` 안내가 나오면 표시된 최소 버전을 확인하세요. 클라이언트는 MCP 설정의 npm 버전을 지원 버전으로 바꾼 뒤 Claude에서는 `/mcp`로 재연결하고 Codex에서는 앱을 다시 시작합니다. 서버가 너무 오래된 경우에는 서버도 지원 버전으로 업데이트해야 합니다. `auth_status`에서 클라이언트·서버 버전과 호환 여부를 확인할 수 있습니다.

0.16 이하 클라이언트는 상세 안내 대신 다음 일반 오류만 표시할 수 있습니다:

> Current session identity or automatic registration is unavailable; verify this MCP client's parent connection.

호환 정책 변경 후 이 오류가 나타나면 `auth_status`로 클라이언트 버전을 확인하고, MCP 설정의 npm 버전을 업데이트한 뒤 Claude는 `/mcp`, Codex는 앱 재시작으로 다시 연결하세요.
