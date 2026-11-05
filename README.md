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

클라이언트 연결에는 HTTPS를 사용하세요. **HTTP 연결 허용**이 꺼져 있으면 `/mcp`와 OAuth 자격증명 경로는 표시 헤더가 없는 평문 요청도 403으로 거부합니다. localhost도 예외가 아닙니다. TLS를 종료하는 proxy 뒤에서는 같은 호스트의 proxy라도 서버에 `--trusted-proxy <proxy CIDR>`를 지정하고, proxy가 외부 입력을 전달하지 않고 `X-Forwarded-Proto`를 단일 원래 scheme 값으로 **덮어써야** 합니다. 기본 신뢰 proxy는 없으며, 신뢰한 proxy의 값이 없거나 중복·목록·잘못된 값이면 HTTPS 증명으로 쓰지 않습니다. 보호된 내부망에서 HTTP를 사용하려면 **인스턴스 설정 → HTTP 연결 허용**을 켜세요.

## 2. 클라이언트 준비

<!-- xbroker-docs:setup -->
### 설치와 MCP 설정

Node.js 18 이상과 npm이 필요합니다. Windows x64, macOS ARM64·x64, Linux x64를 지원합니다. 기본은 게시된 버전을 고정한 전역 설치입니다.

```sh
npm view @xelexis/x-broker version
npm install -g @xelexis/x-broker@0.18.1
x-broker --version
```

예제는 `0.18.1`을 고정합니다. 서버만 바뀐 릴리스는 npm 게시를 생략하므로 서버와 클라이언트 버전이 다를 수 있습니다. 다른 버전은 게시 여부를 확인하고 설치 버전을 바꾸세요. `--version`은 버전 확인이며 대화 연결 검사가 아닙니다.

대안으로 `npx -y @xelexis/x-broker@0.18.1`을 쓸 수 있지만 세션마다 약 100 MB의 npm 프로세스 하나가 계속 남습니다. 이때 아래 `command`를 `npx`로 바꾸고 `args` 앞에 `"-y", "@xelexis/x-broker@0.18.1"`을 추가하세요. `@latest`는 시작 때 레지스트리 확인과 다운로드로 늦어질 수 있으므로 버전을 고정하세요.

macOS·Linux에서는 execve를 지원하는 Node의 전역 wrapper가 client로 교체됩니다. **Windows는 execve가 없어 어느 설치 방식이든 node relay가 남으며, 전역 설치는 npm exec 부모 프로세스를 제거합니다.**

## 3. MCP 설정

기존 설정이 있으면 `x-broker` 항목만 추가하거나 교체하세요. 서버 주소, `project=brk`, `발급받은_토큰`을 실제 값으로 바꾸세요. 토큰이 있는 파일은 Git이나 공유 폴더에 올리지 마세요.

MCP `args`에 `"--tool-profile", "worker"`를 추가하면 모든 하네스에서 관리·버그 조회 도구 7개를 목록에서 숨기고 해당 호출을 `tool-not-in-profile`로 거부합니다. 기본은 `full`이며 서버 권한이나 보안 경계를 바꾸지 않습니다.

**Claude Code — `.mcp.json`**

```json
{
  "mcpServers": {
    "x-broker": {
      "command": "x-broker",
      "args": [
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
command = "x-broker"
args = [
  "--broker-url", "https://broker.example/mcp?project=brk",
  "--token", "발급받은_토큰"
]
```

Codex는 신뢰한 프로젝트의 설정만 읽습니다. 같은 OS 사용자와 인증 상태 디렉터리를 유지하세요. MCP 재연결 후 에이전트에게 이 대화를 연결해 달라고 요청할 때만 `attach_session`을 호출합니다. 기존 등록은 자동 복구합니다. `auth_status`로 등록 이름·clientVersion·serverVersion을 확인하세요. 승인 코드가 나오면 관리 화면에서 승인합니다. 상세 재연결은 `xbroker_docs topic=upgrade`, 연결 오류는 `topic=errors`를 읽으세요.
프로젝트마다 entry를 추가하는 방법은 [여러 프로젝트에 연결하기](#여러-프로젝트에-연결하기)를 보세요. 사용자 지정 `CODEX_HOME`은 각 MCP entry의 `env`에도 같은 경로로 지정합니다.
<!-- /xbroker-docs:setup -->

대화별 클라이언트 상태와 steer 시도 기록은 30일 동안 사용하지 않으면 자동 삭제하며(불확실한 pending 시도는 재연결로 해소될 때까지 보존), 진단 기록은 14일 후 정리합니다.

Windows 클라이언트 0.17.3부터는 `%LOCALAPPDATA%\xelexis\x-broker\client-cache\v1\win32-x64`의 버전·SHA-256별 검증된 사본을 실행하므로, 새 launcher로 시작한 세션을 유지한 채 npm 패키지를 업그레이드할 수 있습니다. **0.17.2 이하의 이전 launcher에서 처음 업그레이드할 때는 실행 중인 asb-client를 한 번 모두 종료하세요.** 실행 중인 세션은 MCP를 다시 시작할 때 새 버전을 적용합니다. 캐시 준비가 실패하면 stderr에 한 줄 안내 후 설치 원본을 실행하므로, 그 세션이 실행 중인 동안은 업그레이드 전에 종료해야 합니다. 새 캐시를 만든 실행은 시작 성공 후 게시 7일이 지난 이전 사본(최대 16개)과 1시간 지난 staging을 정리하며, 잠긴 파일은 남깁니다.

클라이언트 0.17.1에서 `--nickname 이름`으로 연결 시 요청할 통신 이름을 지정할 수 있습니다. 서버가 직접 등록을 지원하고 토큰이 승인 없는 등록을 허용할 때 사용합니다. 이름이 겹치면 대체 이름을 받을 수 있으므로 `auth_status`의 최종 이름을 확인하세요. 직접 등록을 지원하지 않는 서버는 기존 수동 승인 흐름을 사용합니다. 제한 권한·자동 등록 토큰 발급은 인스턴스 관리자가 설정을 켜야 하며 기본값은 꺼짐입니다.

Codex는 신뢰한 프로젝트의 설정을 읽습니다. 기존 실행파일 방식에서 바꿀 때는 서버 주소, 토큰, 지정한 `--auth-dir`을 유지하세요. 같은 OS 사용자와 인증 상태 디렉터리를 사용하세요.

### Codex 재개 실행기 (프롬프트 없는 연결)

macOS·Linux에서 정확한 UUID를 지정한 재개 실행기는 daemon과 embedded 두 모드를 지원합니다. 아래를 `codex-resume.sh`로 저장하고 `sh codex-resume.sh <대화 UUID>`로 실행하세요. `-c model_reasoning_effort=medium` 같은 embedded 옵션을 주면 기존 PID claim 경로를 사용합니다. MCP 설정과 같은 npm client 버전이 필요합니다. 기본 `XB_VERSION=0.18.1`을 실제 MCP 고정 버전에 맞추세요. `--auth-dir`을 따로 썼다면 같은 절대 경로를 `AGENT_SESSION_BROKER_STATE_DIR`로 지정합니다. 사용자·프로젝트 설정은 바꾸지 않습니다.

- embedded 옵션(`-c`·`--config`·`--enable`·`--disable`·`--search`·`--no-daemon`·`--dangerously-bypass-hook-trust`)과 명시 `--remote`는 함께 쓸 수 없습니다. 직접 `codex resume <UUID> ...`를 실행하면 기존 첫 프롬프트 경로를 쓸 수 있습니다.
- `--remote`는 하나만 허용합니다. 기본 daemon은 CODEX_HOME의 socket 별칭을 TUI에 넘기고 helper는 정규 대상의 inode·peer를 검증합니다. 직접 지정한 endpoint는 그대로 쓰며, ws/wss endpoint는 helper 없이 전달합니다. `--last`·`--all`·`--include-non-interactive`는 거절하며 `--` 뒤는 그대로 넘깁니다.
- daemon 경로는 그 CODEX_HOME의 daemon이 없으면 시작합니다(`-c` 없는 `codex`가 자동으로 띄우는 것과 같은 daemon). 시작 실패나 5초 내 socket 미발견 시 helper 없이 일반 재개로 돌아갑니다.
- `-a`·`-s` 같은 권한 옵션은 기본 daemon의 socket 별칭에서 일반 재개처럼 동작합니다. 정규 대상 경로를 직접 `--remote`로 지정하면 Codex가 권한 옵션을 거절할 수 있습니다. daemon 권한은 `config.toml`의 `approval_policy`·`sandbox_mode`로도 설정할 수 있습니다.
- Codex 0.164는 `CODEX_HOME` 자체가 symlink이면 권한 옵션을 넣은 daemon 재개를 거절할 수 있습니다. 권한은 `config.toml`에 설정하거나 symlink가 아닌 home 경로를 사용하세요.
- `HOME` 자체가 symlink이면 `deviceIdentity=directory-insecure`로 장치 holder 식별을 쓰지 못할 수 있습니다. 일반적인 holder 복구가 필요하면 symlink가 아닌 실제 home 경로를 사용하세요.
- daemon helper는 첫 프롬프트와 같은 등록 복구 효과가 있습니다. 진행 중이던 초기 등록·자동 재인증도 이어질 수 있습니다. 인증 흔적이 전혀 없는 새 대화는 등록하지 않습니다. 기존 client에 `receiverReady`가 없으면 준비 완료로 확인하지 않습니다.

```sh
#!/bin/sh
set -eu
umask 077
fail() { printf '%s\n' "$1" >&2; exit 64; }
t=${1:?usage: codex-resume THREAD-UUID [codex args...]}
shift
case "$t" in ????????-????-????-????-????????????) ;; *) exit 64 ;; esac
hex=$(printf '%s' "$t" | tr -d '-')
case "$hex" in *[!0-9a-f]*) exit 64 ;; esac
[ "${#hex}" -eq 32 ] || exit 64
unset CODEX_THREAD_ID
embedded=0 remote= remote_count=0 expect=
for a do
    if [ "$expect" = remote ]; then
        [ "$a" != -- ] && [ -n "$a" ] || fail 'codex-resume --remote requires an endpoint'
        remote=$a expect=
        continue
    fi
    if [ "$expect" = value ]; then expect=; continue; fi
    case "$a" in
        --) break ;;
        --last|--last=*|--all|--all=*|--include-non-interactive|--include-non-interactive=*)
            fail 'codex-resume requires its exact thread UUID; picker selectors are not supported' ;;
        --remote|--remote=*)
            remote_count=$((remote_count + 1))
            [ "$remote_count" -eq 1 ] || fail 'codex-resume accepts only one --remote'
            case "$a" in
                --remote) expect=remote ;;
                *) remote=${a#--remote=}; [ -n "$remote" ] || fail 'codex-resume --remote requires an endpoint' ;;
            esac ;;
        -c|--config|--enable|--disable) embedded=1 expect=value ;;
        -c*|--config*|--enable*|--disable*|--search*|--no-daemon*|--dangerously-bypass-hook-trust*) embedded=1 ;;
    esac
done
[ -z "$expect" ] || fail 'codex-resume option requires a value'
if [ "$embedded" -eq 1 ] && [ "$remote_count" -ne 0 ]; then
    fail 'codex-resume cannot combine a remote daemon with embedded-only options; run codex resume <UUID> ... directly (first-prompt behavior)'
fi
case "$(uname -s)" in Darwin) system=darwin ;; Linux) system=linux ;; *) exit 64 ;; esac
if [ "$embedded" -eq 1 ]; then
    if [ -n "${AGENT_SESSION_BROKER_STATE_DIR:-}" ]; then
        state=$AGENT_SESSION_BROKER_STATE_DIR
    elif [ "$system" = darwin ]; then
        state="$HOME/Library/Application Support/agent-session-broker"
    else
        state="${XDG_CONFIG_HOME:-$HOME/.config}/agent-session-broker"
    fi
    case "$state" in /*) ;; *) exit 64 ;; esac
    d="$state/codex-resume-claims"
    mkdir -p "$d"
    chmod 700 "$d"
    printf '{"v":1,"thread":"%s"}\n' "$t" > "$d/$$.json.tmp"
    mv "$d/$$.json.tmp" "$d/$$.json"
    exec codex resume "$t" "$@"
fi
home=${CODEX_HOME:-$HOME/.codex}
case "$home" in /*) ;; *) home="$PWD/$home" ;; esac
if [ "$remote_count" -ne 0 ]; then
    case "$remote" in
        unix://*) socket=${remote#unix://}; [ -n "$socket" ] || fail 'codex-resume requires an explicit Unix socket path' ;;
        *) exec codex resume "$t" "$@" ;;
    esac
else
    codex app-server daemon start >/dev/null 2>&1 || exec codex resume "$t" "$@"
    socket="$home/app-server-control/app-server-control.sock"
fi
canonical_socket() {
    candidate=$socket
    if [ -L "$candidate" ]; then
        link=$(readlink "$candidate") || return 1
        case "$link" in /*) candidate=$link ;; *) candidate="$(dirname "$candidate")/$link" ;; esac
    fi
    [ ! -L "$candidate" ] && [ -S "$candidate" ] || return 1
    directory=$(CDPATH= cd -P "$(dirname "$candidate")" && pwd -P) || return 1
    canonical="$directory/$(basename "$candidate")"
    if [ "$system" = darwin ]; then
        inode=$(stat -f '%i' "$canonical" 2>/dev/null) || return 1
    else
        inode=$(stat -c '%i' "$canonical" 2>/dev/null) || return 1
    fi
    case "$inode" in ''|*[!0-9]*) return 1 ;; esac
    [ "$inode" != 0 ]
}
tries=0
until canonical_socket; do
    [ "$tries" -lt 50 ] || exec codex resume "$t" "$@"
    tries=$((tries + 1))
    sleep .1
done
helper_socket=$socket
case "$helper_socket" in /*) ;; *) helper_socket="$PWD/$helper_socket" ;; esac
npx -y "@xelexis/x-broker@${XB_VERSION:-0.18.1}" codex-resume-helper \
    --thread "$t" --pid "$$" --codex-home "$home" --socket "$helper_socket" --inode "$inode" \
    </dev/null >/dev/null 2>&1 &
# Rotate the original positional arguments; never join or eval caller input.
remaining=$#
set -- "$@" __xbroker_args_end
parsing=1 added=$remote_count
while [ "$remaining" -gt 0 ]; do
    a=$1; shift
    remaining=$((remaining - 1))
    if [ "$parsing" -eq 1 ]; then
        case "$a" in
            --)
                if [ "$added" -eq 0 ]; then set -- "$@" --remote "unix://$socket"; added=1; fi
                parsing=0 ;;
        esac
    fi
    set -- "$@" "$a"
done
shift
if [ "$added" -eq 0 ]; then set -- "$@" --remote "unix://$socket"; fi
exec codex resume "$t" "$@"
```

`CODEX_THREAD_ID`를 `mcp_servers.x-broker.env_vars`나 `-c` env override로 넘기지 마세요. `/new` 뒤 옛 ID가 남거나 중첩 Codex에 상속될 수 있으며, 프로젝트에 x-broker 설정이 있으면 `-c` env override가 시작·설정 저장을 실패시킬 수 있습니다. 위 실행기는 상속된 ID를 지웁니다. embedded에서만 자신의 PID에 묶인 일회용 claim 파일을 쓰며, daemon에서는 검증한 socket을 통해 정확한 U의 auth_status를 호출합니다. client는 정확한 rollout·프로세스·기존 등록을 확인하고, 첫 도구 호출의 thread metadata로 확정합니다. ID가 다르면 기존 수신과 lease를 먼저 해제합니다. claim만으로 새 등록이나 승인을 만들지 않습니다.

지원 범위는 새 프로세스의 **최초 exact resume**입니다. Windows, 실행기 없는 resume, TUI 안의 `/resume`·fork 등 전환은 기존 첫 프롬프트 대체 경로를 사용합니다. 이 대체 경로는 첫 x-broker 도구 호출에서 대화를 식별합니다. 아래 수명 주기 hook을 설치했다면 프롬프트를 한 번 입력하고, 없으면 모델에게 그 대화에서 `auth_status`를 한 번 호출하도록 요청하세요. 최초 MCP가 claim을 소비하기 전에 `/new`로 만든 V가 U의 미확정 claim을 소비해도, 양쪽 client가 이 양보 기능을 지원하고 **서버가 `message.ack.v1`을 지원해 해당 연결에서 ACK가 활성인 경우(서버 0.17.3 이상)** U의 첫 x-broker 호출이 몇 초 안에 넘겨받습니다. ACK가 활성이지 않으면 U는 계속 수신하지만, U 자신의 MCP는 V의 첫 도구 호출이나 종료까지 발신하지 못할 수 있습니다.

사용자 지정 `CODEX_HOME`을 쓰면 daemon이 MCP 환경에서 이를 제거하므로, 같은 daemon home을 MCP 설정에도 명시하세요(필요하면 `HOME`도 함께 지정). `CODEX_THREAD_ID`는 넣지 않습니다.

```toml
[mcp_servers.x-broker.env]
CODEX_HOME = "/absolute/path/to/codex-home"
```

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

MCP 설정과 같은 고정 버전을 `npm install -g @xelexis/x-broker@0.18.1`로 설치하고, `command -v x-broker`가 출력한 절대 경로를 아래 hook 명령에 사용하세요. hook의 `PATH`에서 `node`를 찾을 수 있어야 하며, 업그레이드할 때도 전역 설치 버전을 MCP 설정과 같게 유지하세요.

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

### 여러 프로젝트에 연결하기

한 대화에서 프로젝트마다 MCP entry를 하나씩 추가합니다. entry 이름, broker URL의 `?project=`와 토큰을 각각 구분하고, 사용할 프로젝트의 entry에서 `attach_session`·`auth_status`·`send_message`를 호출하세요. 등록 이름과 권한은 프로젝트마다 따로 확인합니다.

프로젝트별 토큰은 해당 프로젝트의 entry에만 넣으세요. 토큰을 포함한 설정을 Git·공유 폴더·메시지·진단 로그에 올리지 말고, 아래 예제의 토큰 자리만 로컬에서 바꾸세요. 서버는 교차 프로젝트 전송을 거부합니다. 다만 **같은 대화의 모델 context에는 여러 프로젝트의 정보가 함께 들어가며, 모델이 그 정보를 다른 프로젝트에 다시 보낼 수 있습니다.** 서로 정보를 공유하면 안 되는 프로젝트는 대화를 나누세요.

고정 버전 전역 설치(`npm install -g @xelexis/x-broker@0.18.1`)를 권장합니다. entry마다 client 프로세스가 하나씩 생기며, npx는 npm 부모도 남깁니다. 다음은 macOS ARM64, Node 24.21.0/npm 11.19.0, client 0.18.0의 RSS 합계입니다. 3초 안정화 후 10표본의 중앙값이며 하네스·모델·서버 메모리는 제외했습니다.

| 실행/상태 | entry 1개 | entry 2개 | 남은 프로세스 수 1개→2개 |
| --- | ---: | ---: | --- |
| 전역 / 초기화 전 | 18.62 MiB | 37.05 MiB | 1→2 |
| 전역 / 등록 후 | 20.05 MiB | 39.17 MiB | 1→2 |
| 전역 / 수신 후 | 20.45 MiB | 39.22 MiB | 1→2 |
| npx / 초기화 전 | 120.41 MiB | 237.08 MiB | 2→4 |
| npx / 등록 후 | 72.47 MiB | 197.86 MiB | 2→4 |
| npx / 수신 후 | 72.88 MiB | 197.89 MiB | 2→4 |

RSS는 공유 페이지를 중복 계상하며 시작 시점·GC·플랫폼에 따라 달라집니다. npx 부모만 약 52–102 MiB/entry로 관측돼 고정 100 MB는 아닙니다. 수신 후 표본을 10대화×2프로젝트로 선형 확대하면 전역 약 392 MiB, npx 약 1,979 MiB입니다. 실제 10대화 부하 시험이나 고유 물리 메모리 측정은 아닙니다. Windows는 전역 설치도 node relay가 남습니다.

**Claude Code·Kimi — `.mcp.json`**

다음은 Kimi에도 사용할 수 있도록 상태 디렉터리를 나눈 예제입니다. Claude는 동일 상태 디렉터리를 공유해도 프로젝트별 등록이 분리됩니다. 경로는 사용자 소유의 서로 다른 절대 경로로 바꾸세요.

```json
{
  "mcpServers": {
    "x-broker-p1": {
      "command": "x-broker",
      "args": ["--broker-url", "https://broker.example/mcp?project=p1", "--token", "프로젝트_P1_토큰", "--state-dir", "/absolute/path/client-state-p1"]
    },
    "x-broker-p2": {
      "command": "x-broker",
      "args": ["--broker-url", "https://broker.example/mcp?project=p2", "--token", "프로젝트_P2_토큰", "--state-dir", "/absolute/path/client-state-p2"]
    }
  }
}
```

**Codex — `.codex/config.toml`**

```toml
[mcp_servers.x-broker-p1]
command = "x-broker"
args = ["--broker-url", "https://broker.example/mcp?project=p1", "--token", "프로젝트_P1_토큰"]

[mcp_servers.x-broker-p2]
command = "x-broker"
args = ["--broker-url", "https://broker.example/mcp?project=p2", "--token", "프로젝트_P2_토큰"]
```

Codex의 다섯 수명 주기 hook에는 **각 entry의 handler를 모두** 넣으세요. 한 entry의 hook은 다른 entry의 pending 메시지를 비우지 않습니다. 아래 `.codex/hooks.json`은 client 0.17.2 이상용이며, hook 정의는 Codex에서 검토·신뢰한 뒤 사용하세요.

```json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [
      {"type": "mcp_tool", "server": "x-broker-p1", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10},
      {"type": "mcp_tool", "server": "x-broker-p2", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10}
    ]}],
    "PreToolUse": [{"matcher": "*", "hooks": [
      {"type": "mcp_tool", "server": "x-broker-p1", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10},
      {"type": "mcp_tool", "server": "x-broker-p2", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10}
    ]}],
    "PostToolUse": [{"matcher": "*", "hooks": [
      {"type": "mcp_tool", "server": "x-broker-p1", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10},
      {"type": "mcp_tool", "server": "x-broker-p2", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10}
    ]}],
    "Stop": [{"hooks": [
      {"type": "mcp_tool", "server": "x-broker-p1", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10},
      {"type": "mcp_tool", "server": "x-broker-p2", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}", "turn_id": "${turn_id}"}, "timeout": 10}
    ]}],
    "Interrupt": [{"hooks": [
      {"type": "mcp_tool", "server": "x-broker-p1", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}"}, "timeout": 10},
      {"type": "mcp_tool", "server": "x-broker-p2", "tool": "ingress_hook", "input": {"session_id": "${session_id}", "hook_event_name": "${hook_event_name}"}, "timeout": 10}
    ]}]
  }
}
```

macOS의 Codex 0.164.0 embedded에서 1 entry, 2 entries, 1 entry+단순 MCP, 2 entries/hook 없음, 2 entries/entry별 hook의 실제 입력·등록·`auth_status`를 확인했습니다. 두 entry 때문에 시작이 멈추는 현상은 재현되지 않았습니다. 이 시험은 전체 메시지 경로의 장기 신뢰성이나 최소 Codex 버전을 정하지 않습니다.

사용자 지정 `CODEX_HOME`을 쓰면 **각 MCP 자식에도 같은 절대 경로를 명시**하세요. CLI의 환경변수가 자식에게 자동 전달된다고 가정하면 `codex session not found`가 발생할 수 있습니다. 위 두 MCP 설정에 다음을 덧붙입니다. 기본 홈을 쓴다면 이 추가 설정은 필요하지 않습니다.

```toml
[mcp_servers.x-broker-p1.env]
CODEX_HOME = "/absolute/path/codex-home"

[mcp_servers.x-broker-p2.env]
CODEX_HOME = "/absolute/path/codex-home"
```

자동화한 PTY에서는 안쪽 터미널의 행·열 크기와 raw 입력을 설정하세요. 시험 중 Expect의 안쪽 PTY가 0×0이어서 화면 키워드를 놓쳤고, 바깥 PTY가 Enter의 CR을 LF로 바꿔 전송하지 못했습니다. 이 하네스 설정을 고친 0.164.0에서 다섯 변형이 모두 통과했으며, 이 결과로 Codex 업그레이드가 필요하다고 판단하지는 않았습니다.

**Kimi — entry별 상태 디렉터리와 helper**

같은 Kimi 부모 PID와 상태 디렉터리를 공유하면 두 번째 hook 소켓이 충돌해 `kimi-hook-unavailable`이 됩니다. 위 `.mcp.json`처럼 상태 디렉터리를 나누고, Kimi의 `config.toml`에도 각 entry와 같은 경로의 helper를 설정하세요. 토큰은 helper 명령에 넣지 않습니다. 전역 설치된 `x-broker`의 절대 경로를 사용합니다.

```toml
[[hooks]]
event = "SessionStart"
command = '"/absolute/path/x-broker" kimi-hook --state-dir "/absolute/path/client-state-p1"'
timeout = 5

[[hooks]]
event = "SessionStart"
command = '"/absolute/path/x-broker" kimi-hook --state-dir "/absolute/path/client-state-p2"'
timeout = 5

[[hooks]]
event = "UserPromptSubmit"
command = '"/absolute/path/x-broker" kimi-hook --state-dir "/absolute/path/client-state-p1"'
timeout = 5

[[hooks]]
event = "UserPromptSubmit"
command = '"/absolute/path/x-broker" kimi-hook --state-dir "/absolute/path/client-state-p2"'
timeout = 5

[[hooks]]
event = "Stop"
command = '"/absolute/path/x-broker" kimi-hook --state-dir "/absolute/path/client-state-p1"'
timeout = 5

[[hooks]]
event = "Stop"
command = '"/absolute/path/x-broker" kimi-hook --state-dir "/absolute/path/client-state-p2"'
timeout = 5
```

Kimi 수신은 다음 eligible UserPromptSubmit/Stop 경계에서 이루어지며 idle 대화를 깨우지 않습니다. **Kimi는 첨부를 받을 수 없습니다.** 첨부를 지원하는 Claude·Codex 수신자에게 보내는 것은 가능합니다.

## 4. 연결 확인

1. Claude Code 또는 Codex의 MCP 연결을 다시 시작합니다.
2. `이 대화를 x-broker에 연결해 줘`라고 요청합니다.
3. 승인 코드가 나오면 관리 패널의 `/auth/code`에서 대화를 확인하고 승인합니다. `session:register:auto` 권한이 있는 토큰은 이 연결 요청 시 승인 절차 없이 등록합니다.
4. `auth_status`로 등록 상태와 최종 이름을 확인하고, `x-broker에 연결된 세션을 보여줘`라고 요청해 목록에서 현재 세션을 확인합니다.

이 연결 요청 방식은 클라이언트 0.17.1부터 적용됩니다. 새 대화가 시작되는 것만으로 등록하지 않습니다. 0.17.0 이하 client는 시작 시 자동 등록을 시도하는 기존 동작을 유지합니다.

연결되지 않으면 `x-broker --version`(npx 사용자는 고정 버전의 `--version`), 서버 주소, 프로젝트 접속 허용, 토큰 상태를 확인하세요. 최초 다운로드가 늦으면 2단계의 `--version` 명령을 먼저 실행하세요.

업데이트 전에는 서버를 중지하고 데이터 디렉터리를 백업하세요. [업그레이드 안내](https://github.com/xelexis-dev/agent-session-broker-deploy/blob/main/UPGRADE_PATH.md)를 확인하고 같은 데이터 경로를 유지하세요.

### 대화를 재개해도 연결 유지

클라이언트 0.17.1은 `claude --resume` 또는 새로 시작한 Claude 안에서 `/resume`으로 대화를 재개하면 `/mcp` 조작 없이 같은 등록과 이름을 이어 씁니다.

- 서버도 0.17.1이면 `/clear` 뒤 새 대화로 등록을 인계합니다. `/resume`으로 원래 대화에 돌아오면 등록을 다시 가져옵니다.
- `claude --bg`로 실행한 백그라운드 세션, `/resume`으로 붙은 뷰어, `claude stop` 후 `claude --resume`도 연결을 이어 갑니다.
- 구서버에서는 `/clear` 뒤 등록을 인계하지 않습니다. 그동안 도착한 메시지는 보류하고 원래 대화로 `/resume`한 뒤 전달합니다. 원래 대화로 돌아오기 전에 Claude를 종료하면 보류한 메시지는 전달되지 않습니다.

수동 승인 토큰(자동 등록 권한 없음)은 `/clear`나 대화 전환 뒤 자동으로 인계하지 않습니다. 새 대화에서 사용자가 연결을 요청하면 승인 링크가 나오고, 승인하면 기존 등록의 이름, 등록 ID, 대기 메시지를 이어받습니다. 승인 화면에는 임시 이름(`<이름>-next`)이 보이며 승인 뒤 원래 이름으로 바뀝니다. 서버와 클라이언트 모두 0.17.1이 필요합니다. 설정 파일에 고정한 세션 자격은 인계를 지원하지 않습니다.

### 무응답 세션 등록

통신이 끊긴 등록은 목록에 `missing`(응답 없음)으로 남아 재연결할 수 있습니다. 다만 마지막 통신 후 30일 이상이고 상태 확인 probe 기한도 지난 비정지 등록은 자동으로 연결 해제됩니다. 이후 약 1시간 10분이 지나면 기존 정리 경로가 기록을 제거합니다. 일시 중지된 등록은 제외하며 재시작 유예와 순차 처리 때문에 정리가 늦어질 수 있습니다. 기록이 남아 있는 동안에는 같은 등록 ID와 이름을 이어 쓸 수 있고, 연결 해제 상태에서도 제거 전까지 등록의 이름을 예약합니다.

기록 제거 시 정리 후 명시 재승인을 지원하는 현재 holder의 자동 승인 증명이 정확히 맞으면 바인딩과 교환 기록을 해제하고, 해당 세션 자격이 아직 유효할 때만 회수합니다. 이미 만료·회수되었거나 보존 기한이 지나 자격이 없어도 일치하는 자동 바인딩은 정리됩니다. 수동 승인·구 client·증명이 맞지 않는 경우에는 제어 상태를 보존하므로 모든 이름이나 자격의 해제를 보장하지 않습니다. 기록이 제거된 대화는 사용자의 명시적 `attach_session` 요청으로 재승인을 받습니다. 등록 상한은 1,024개이며 필요한 경우 관리자에게 연결 해제 또는 retire를 요청하세요.

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
| `session:manage` | 세션 관리 | stop_session으로 이 세션의 연결을 해제하며, stop_session·retire_session·suspend_session·unsuspend_session으로 토큰 소유자가 관리할 수 있는 다른 세션의 연결을 해제·일시 중지·재개합니다. retire_session은 등록과 사용한 세션 자격을 회수해 이름 예약을 해제합니다. 자기 retire와 이 세션의 일시 중지·재개는 허용되지 않습니다. 활성 인스턴스 관리자 소유 토큰은 list_bug_reports·get_bug_report·set_bug_report_status로 현재 프로젝트 세대의 버그 리포트를 조회·처리할 수 있습니다. |
| `session:read` | 세션 조회 | list_sessions와 get_session으로 프로젝트 세션을 조회합니다. |
| `session:register` | 등록·연결 유지 (필수) | attach_session·register_session·resume_session·renew_lease·probe_response·report_ingress_failure로 자기 세션을 등록하고 연결을 유지합니다. |
| `session:register:auto` | 연결 요청 시 승인 없이 등록 | 사용자가 이 대화의 연결을 요청하면 승인 절차 없이 등록합니다. 새 대화가 시작되는 것만으로 등록하지 않습니다. 프로젝트 토큰으로 사람의 승인 없이 직접 등록을 요청하며 세션 자격증명에는 위임되지 않습니다. |
| `session:rename` | 자기 이름 변경 | rename_session으로 자기 세션의 통신 이름을 변경합니다. |
| `session:spawn` | 세션 생성 | spawn_session 호출 권한이며 현재 원격 서버는 프로세스를 시작하지 않고 지원하지 않는다는 안내를 반환합니다. |

전체 기록은 client 인증 상태 디렉터리(`--auth-dir`) 아래 `diagnostics/v2/<binding-key>.json`에 저장됩니다. 잠금도 `diagnostics/v2/<binding-key>.lock`을 써서 구 client의 prune과 분리합니다. 기존 `diagnostics/<binding-key>.json`은 0.17.2 롤백용으로 쓰기를 멈추고, 조회할 때만 함께 읽습니다. 0.17.2로 내리면 v2 기록은 보이지 않으며 구 client는 v1 기록만 갱신합니다. 새 client로 돌아오면 두 기록을 다시 합쳐 봅니다. 알 수 없는 v2 확장 필드는 저장 시 보존하고, 화면에는 알려진 코드만 표시합니다. 파일은 최근 256건·최대 128 KiB, 권한 0600이며 갱신 성공은 요약 시각만 갱신합니다. 토큰·URL·실행 인자·메시지 본문·오류 원문은 담지 않습니다. 기록 저장 실패는 연결을 중단하지 않으며 강제 종료 순간의 종료 사유는 기록되지 않을 수 있습니다.

### 세션 관리 권한

서버 0.17.1부터 `session:manage`로 자기 연결 해제와 소유권이 허용하는 다른 세션의 관리가 가능합니다. 기존 토큰도 같습니다.

일시 중지 등록은 제외하며, 마지막 통신 후 30일과 probe 기한을 모두 넘은 등록은 자동 분리한 뒤 약 70분 후 정리합니다. 재시작 유예와 순차 처리로 지연될 수 있고 이름·자격 해제는 조건부입니다.

- Owner 토큰은 같은 프로젝트의 모든 세션을 관리합니다. Developer 토큰은 같은 소유자의 세션만 관리합니다.
- 이 세션 자신은 `stop_session`으로 연결 해제만 할 수 있습니다. 자신의 `suspend_session`·`unsuspend_session` 호출은 허용되지 않습니다. 소유자 정보가 없는 기존 토큰도 자기 연결 해제만 할 수 있습니다.
- `stop_session`은 대상 프로세스를 종료하지 않고 연결을 해제하며 대기 메시지를 비웁니다. 재승인 가능한 현재 holder의 자동 자격은 행 정리 때 회수하며, 나머지 자격은 만료 또는 `retire_session`까지 이름을 예약합니다. 대상 대화의 사용자가 다시 연결을 요청할 때만 등록됩니다.
- `suspend_session`은 관리할 수 있는 다른 세션의 연결을 일시 중지하고 대기 메시지를 버리며 진행 중 요청을 취소합니다. `unsuspend_session`은 그 세션을 재개하며 대상은 다음 lease부터 다시 연결됩니다.
- 다른 프로젝트의 세션은 관리할 수 없습니다. 권한은 매 호출 시 현재 역할·소유권·토큰 상태로 다시 확인하므로 역할 강등·멤버 제외·토큰 회수도 반영됩니다.

`retire_session`은 클라이언트와 서버 모두 0.17.3 이상에서 지원합니다. 클라이언트는 고정된 도구 목록을 사용하므로 구 client를 재연결하는 것만으로 새 도구가 추가되지 않습니다.

`stop_session`은 다시 attach할 수 있는 연결 해제입니다. `retire_session`은 다른 세션의 등록과 연결 이력이 있는 세션 자격을 회수하여 이름 예약을 해제합니다. 프로세스를 종료하지 않으며 프로젝트 토큰과 연결하지 않은 대체 자격은 보존합니다. 자기 자신과 일시 중지된 대상은 retire할 수 없습니다.

| 도구 | 동작 |
| --- | --- |
| `xbroker_docs {topic?}` | client 0.17.3의 로컬 읽기 전용 도움말(서버 업데이트 불필요). 인증·등록·서버 호출 없이 목차 또는 주제 본문과 clientVersion을 반환합니다. |
| `stop_session {name}` | 연결과 대기 메시지를 정리합니다. 재승인 가능한 현재 holder의 자동 자격은 기록 제거 직전에 회수하며, 나머지는 이름 예약을 유지합니다. |
| `retire_session {registrationId}` | 정확한 등록과 그 등록에 바인딩된 세션 자격을 회수합니다. |
| `retire_session {name}` | 등록 없이 이름을 예약한 자격 중 과거 연결 이력이 있는 자격만 회수합니다. |

`registrationId`와 `name` 중 정확히 하나를 지정합니다. 이름을 보유한 등록이 있으면 ID를 확인해 호출하세요. 미사용 자격은 관리 화면 또는 만료로 정리합니다. `cleanup-required`는 연결 해제 뒤 저장이 끝나지 않은 상태이며 응답의 같은 `registrationId`로 재호출합니다. name 모드는 **호출 시점**의 고아 자격을 대상으로 하므로 결과가 불명하면 바로 재시도하지 말고 `list_sessions`와 rename으로 먼저 확인하세요. 성공 결과의 `revokedCredentials`에는 회수한 자격의 비밀이 아닌 ID와 첫 연결 시각이 표시됩니다.

rename_session의 nickname-in-use는 holder에 따라 live-session·inactive-registration·detached-registration(등록 확인 후 ID retire), orphaned-credential(name retire), unused-credential(패널 또는 만료)로 안내합니다. 구서버가 사유를 주지 않으면 server gave no reason을 표시합니다.

정리로 자동 자격이 회수된 대화는 사용자가 명시적으로 `attach_session`을 호출할 때만 부모 토큰으로 새 자격과 등록을 요청합니다. 가능한 경우 저장된 이름을 요청하며, 네트워크 오류만으로 옛 등록 증명을 지우거나 자동으로 대화를 되살리지 않습니다. 같은 대화라도 새 등록 ID를 받으므로, 이전 상대는 `recipient-changed`를 받을 수 있습니다. 상대가 `get_session`으로 이름의 현재 등록을 확인한 뒤 다시 보내야 합니다. 관리자 분리 뒤에도 부모가 허용하면 명시 attach로 새 등록이 가능하므로, 이를 막으려면 부모 토큰 회수 또는 수동 승인 정책을 사용하세요.

`suspend_session`·`unsuspend_session`은 클라이언트 0.17.1에서 도구 목록에 표시됩니다. 실행 중인 0.17.0 클라이언트는 기존 도구 목록을 유지합니다. 기존 `stop_session`으로 다른 세션을 해제하는 기능은 서버만 0.17.1로 올려도 권한 범위 안에서 사용할 수 있습니다.

관리 화면의 **세션 감사**에서 관련 이력을 확인할 수 있습니다. 감사 화면의 활성화 조건은 기존과 같습니다. 자동 자격 정리의 `revoked/explicit-release`는 앞선 명시적 stop에 따른 정책 결과이며, 목록 조회 때 사람이 토큰 회수 버튼을 눌렀다는 뜻은 아닙니다. 기존 고아 행을 일괄 회수하지 않으며 자연 만료에 맡깁니다. 0.17.2로 내리면 저장 형식은 읽을 수 있지만 이미 회수한 자격이 복구되지는 않습니다. 구 서버가 등록을 다시 쓰면 재승인 capability를 버리므로 재업그레이드 뒤에도 새 holder가 광고하기 전까지 자동 회수 대상에서 제외됩니다.

### Codex 실행 방식

프로젝트에 맞춰 daemon과 embedded 모드를 선택하고, 한 대화에서는 모드를 유지하세요. Codex 0.164.0에서는 `codex` 또는 `codex resume <대화 UUID>`를 `-c`, `--enable`, `--disable`, `--search` 없이 실행하면 CODEX_HOME별 공유 daemon이 자동 시작됩니다. 모델·effort는 `-c` 대신 `config.toml`에 설정합니다. daemon은 `codex app-server daemon start`, `stop`, `restart`, `version`으로 관리합니다.

daemon 모드의 hook·MCP 서버는 daemon 환경에서 실행되므로 TUI를 여는 셸의 환경변수·`-c` 옵션은 적용되지 않습니다. hook·MCP에 필요한 대화별 값은 `config.toml`(예: MCP 서버의 `env`)에 설정하거나 embedded(`-c`)를 사용하되, `CODEX_THREAD_ID`는 넣지 마세요.

daemon 즉시 전달은 **`message.ack.v1`을 지원하는 서버(0.17.3 이상)와 Codex 수명 주기 hook**이 있어 ACK가 활성인 연결에서만 동작합니다. 실행 중인 도구에는 즉시, 생성 중에는 hook 경계를 최대 10초 기다린 뒤 `turn/steer`로 메시지를 넣습니다. 그 밖에는 기존 도구 경계 전달을 사용합니다. 생성 중 주입하면 화면의 응답이 다시 써질 수 있고, 메시지가 계속 오면 재시작이 여러 번 생길 수 있습니다. 실행 중 명령은 유지됩니다. 기본 켜짐이며 client 인자 `--codex-steer off`로 끌 수 있습니다(`--codex-steer on`으로 켬). 새 steer 전에 읽기 전용 실험 API `thread/queue/list` 지원을 확인합니다. 지원하지 않으면 해당 binding의 steer를 `unsupported-codex`로 끄고 기존 hook·queue 경로를 사용합니다.

- 결과가 불확실한 steer는 본문 없는 시도 기록을 유지합니다. `codex app-server daemon stop`·`restart`나 client 재시작, 같은 등록의 lease·binding 교체 뒤에도 확인된 thread 전체에서 정확한 `clientId`와 envelope를 찾아 연속 구간만 ACK합니다. 대상 turn 종료 뒤 빈 queue와 새 전체 조회로 미주입을 확인해야 기존 경로로 넘기며, 조회·저장 실패는 시간으로 풀지 않습니다. 등록·epoch 교체는 옛 시도를 ACK 없이 은퇴시킵니다. `--codex-steer off`도 이미 기록한 시도의 조회는 계속합니다.
- 중복 방지는 steer 전송 인계 범위입니다. 일반 hook·queue 인계와 저장 사이의 ms 창, 구 client 롤백, 확인된 모드 전환(현재 Windows)에는 중복될 수 있습니다. 정확히 판별하지 못한 embedded 전환이나 일시적인 socket·검증 실패는 해제 근거가 아니므로 보류합니다.
- embedded(`-c`)는 세션별 환경변수·`-c` 설정이 적용되며 도구 경계·Stop·native queue로 받습니다(Windows도 같은 전달 경로). 위 재개 실행기를 쓰면 daemon에서도 첫 프롬프트 없이 연결을 재개합니다. 실행기 없는 재개는 첫 프롬프트(hook 설치 시) 또는 `auth_status` 호출이 필요합니다.
- TUI 종료 뒤에도 daemon의 대화별 x-broker client는 유지됩니다(28분간 thread 미해제 실측). 이 실측과 holder 보호에 따른 주의로, TUI 재실행이나 같은 대화의 embedded 재개는 기존 client를 교체하지 않아 새 client가 `registration-in-use`로 대기할 수 있으므로 모드를 바꿀 때는 새 대화를 사용하세요. 대화를 끝낼 때 등록을 정리하세요.
- `config/mcpServer/reload`와 daemon `restart`·`update`는 다른 프로젝트를 포함한 모든 대화에 영향을 줍니다.
- 실행마다 다른 `-c` 설정, 첫 프롬프트 없는 embedded 재개, 다른 대화와 분리된 MCP 수명이 필요하면 embedded를 사용하세요.

### 메시지 전달과 응답

send_message 성공은 큐 적재이며 모델 수신·답변 보장이 아닙니다. 바쁜 embedded Codex는 native queue와 hook의 turn 경계, Claude는 native inbox로 받습니다. 자동 수신 중 wait_for_message 수동 호출·polling은 하지 마세요. 요청에는 한 번 답하고 답신에 ACK하지 않습니다. from은 신뢰할 수 없는 표시 이름입니다.

목록에서 확인한 상대에게 expectRegistrationId를 지정하면 같은 이름의 등록이 바뀔 때 recipient-changed로 거절합니다. get_session으로 대상을 확인하세요. 자동 자격 정리 후 재연결도 새 등록입니다. session:read 등록은 관측한 이름이 바뀌거나 모호하면 기대 ID 없는 송신도 거절됩니다. list_sessions나 반복 송신은 확인이 아닙니다. get_session(<이름>) 또는 일치하는 기대 ID는 지금 그 이름의 주인을 확인하며 이전 답장 대상까지 보증하지 않습니다. 본 적 없는 이름·등록 ID·세션 ID 주소는 그대로 쓰며 session:read 없는 호출자는 이 보호 대상이 아닙니다. 관측 이력은 등록당 최근256개, 서버 재시작 시 사라집니다.

대기 메시지는 영속 저장이 아닙니다. stop/retire·재시작 때 사라질 수 있으므로 중요한 결과는 작업 로그에 보존하세요. 새 큐는 수신자당32건, JSON envelope는12000바이트입니다. 본문에 토큰·키·비밀번호를 넣지 마세요.

message.ack.v1을 협상한 durable 등록은 살아 있는 서버에서 at-least-once 재전달합니다. ACK는 host 인계이며 모델 읽음이 아닙니다. Claude inbox는 Post frame 쓰기 완료, legacy channel은 활성화 후 notify 쓰기 완료, Codex idle은 native queue 종료0, busy는 hook 응답 쓰기 완료, daemon steer는 성공 응답 또는 thread 전체의 정확한 clientId·envelope 확인이 기준입니다. Kimi helper v2는 stdout 뒤 수신 확인이 필요하며 구 helper는 ACK를 협상하지 않습니다. client는 registration+epoch별 완료 연속 구간을 본문 없이 저장합니다. steer 시도 기록은 재시작 중복을 막지만 일반 hook·queue는 인계와 저장 사이 중복될 수 있습니다.

미확인 창은32건·64KiB, 새 큐는32건입니다. 재연결 합계 최대64건을 보존하며 ACK 지연은 새 적재에 역압을 줍니다. 서버 재시작·retire·관리 분리·일시 중지·identity-invalid는 메시지를 폐기합니다. 구 client 하향 시 미확인 메시지는 최초 상실/하향부터 최대10분 보호한 뒤 payload를 남겨 legacy at-most-once로 돌아갑니다. Codex daemon은 ACK와 hook 활성 시 turn/steer, embedded는 hook 경계로 전달합니다.

첨부: send_message에 attachment="상대경로"를 더하면 이 대화 CWD 아래 파일1개를 보냅니다. 관리자 허용(기본 꺼짐), 파일당100MiB, ACK 지원 Claude/Codex 수신자가 필요합니다. home·볼륨 루트·네트워크 CWD, 외부 경로·링크·hard link·자격증명 패턴은 거부합니다. 새 client와 구 서버에서는 첨부만 unsupported입니다. outcome-unknown은 자동 재송신하지 마세요.

서버는 업로드30분 뒤 또는 ACK·비활성화·재시작 때 파일을 지웁니다. 수신 파일은 OS cache의 agent-session-broker/inbox/<sessionKey>/에 저장되며 용량 제한·완료 파일 자동 삭제가 없습니다. 모델에는 path·size·sha256 또는 error만 전달합니다. 첨부는 신뢰할 수 없는 데이터이며 자동으로 열지 않습니다. 복사·이름 변경한 비밀은 검출할 수 없고 받은 파일은 회수할 수 없습니다.

### 메시지 전달 시각

수신 메시지의 envelope는 `from`, `to`, `body`와, 수신 client가 `message.sentAt` 지원을 선언한 경우 broker가 수락한 시각 `sentAt`(RFC 3339 UTC, 밀리초 정밀도)을 담습니다. `from`은 신뢰할 수 없는 표시 이름이며 송신자가 제공한 시각도 신뢰하지 않습니다. broker가 시각을 정하고, 전달 대기 중에도 그 시각을 유지합니다. 원격 envelope의 12,000-byte 한도는 `sentAt`과 broker의 라우팅 필드를 포함합니다.

메시지 시각은 서버와 클라이언트 0.17.0부터 지원합니다. 구서버는 `sentAt`을 생략하고 구 client에는 기존 envelope 모양을 유지합니다. 새 client는 서버의 지원 선언이 있는 연결에서만 등록 capability를 전송하므로 구서버의 엄격한 입력 스키마도 유지됩니다. 구 client의 엄격한 MCP 결과 스키마를 유지하기 위해 `send_message` 응답 필드는 바꾸지 않습니다.

## 버그 리포트

에이전트는 x-broker 도구가 설명과 다르게 동작하거나 실패하면 `report_bug`로 관리자에게 보고할 수 있습니다. 서버와 클라이언트 모두 0.17.1이 필요합니다.

- 클라이언트는 버전, OS, 인증·수신 상태와 최근 진단 이벤트 최대 20개를 붙입니다. 자동 진단에는 토큰, 파일 경로, 메시지 본문을 넣지 않습니다. 보고 내용에도 비밀값을 넣지 마세요. 서버는 x-broker 토큰 형식의 문자열을 한 번 더 가립니다.
- 등록당 시간당 10건, 프로젝트당 하루 200건까지 받습니다. 제한에 걸리면 재시도 시각을 안내합니다.
- 관리자는 **관리자 전용 → 버그 리포트**에서 내용을 확인하고 닫거나 다시 열 수 있습니다.
- 인스턴스에 최대 2,000건을 180일까지 보관합니다. 개수나 기간을 넘으면 오래된 것부터 지웁니다. 프로젝트를 삭제하면 해당 리포트도 삭제합니다.

`auth_status.codexDelivery`의 mode/reason으로 전달 경로를 확인합니다. `steer-unchecked`는 첫 호스트 검증 전의 정상 상태입니다. `unverified-host`는 검증 실패이며, Windows stub에서는 검증 없이 항상 hook을 쓴다는 예외입니다. POSIX embedded는 `hook/steer-unchecked`에서 검증 실패 후 `hook/unverified-host`로 바뀝니다. `mode=hook`만으로 daemon 미지원이라 판단하지 마세요. `steer-uncertain`·`steer-recovery-pending`은 전송 인계 확인 중이며 FIFO 뒤도 보류합니다. `steer-recovery-unavailable`은 시도 기록을 안전하게 읽거나 쓸 수 없는 상태입니다. 기록을 지우거나 확인 없이 다시 보내지 마세요. 재시작·같은 등록의 lease 교체도 보류를 유지하고, 등록·epoch 교체는 옛 시도를 은퇴시킵니다. `--codex-steer off`는 새 steer만 끕니다. 보호 범위와 모드 전환의 한계는 [Codex 실행 방식](#codex-실행-방식)을 보세요.

실행기 없이 재시작한 idle 대화는 threadId가 담긴 첫 tools/call(예: `auth_status`) 전까지 복구 조회를 기다립니다. 진단의 `steer-recovery-ambiguous`는 같은 clientId의 내용을 검증하지 못한 보류입니다.

<!-- xbroker-docs:upgrade -->
## 연결된 채 업그레이드

이번 릴리스의 권장 client는 0.18.1입니다. 0.18.1은 문서 업데이트이므로 기존 0.18.0 client의 갱신은 선택 사항입니다. 파일 첨부에는 서버와 송신·수신 client 모두 0.18.0 이상이 필요합니다.

`auth_status.update`는 연결한 서버가 알려 준 `recommendedClientVersion`보다 현재 `clientVersion`이 낮을 때만 표시됩니다. 서버 버전과 npm client 버전은 별개이며, 구서버가 권장값을 주지 않으면 안내를 표시하지 않습니다. 이 값은 인터넷의 latest가 아니라 서버 릴리스에서 게시 여부를 검증한 권장 버전입니다.

전역 설치 사용자는 `npm install -g @xelexis/x-broker@<권장 버전>`으로 갱신하고 `x-broker --version`을 확인한 뒤 아래 방법으로 재시작하거나 재연결하세요. npx 사용자는 MCP 설정의 고정 버전을 권장 버전으로 바꾸고 `npx -y @xelexis/x-broker@<권장 버전> --version`으로 준비합니다. 전역 설치 갱신만으로 별도의 npx-pin은 바뀌지 않습니다. `--version`은 버전 확인이며 대화 연결 갱신이 아닙니다.

- **Claude:** 설치 또는 설정 버전을 갱신한 뒤 해당 대화에서 `/mcp` → `x-broker` → `Reconnect`를 실행합니다. 도구 목록과 실제 `clientVersion`이 갱신됐는지 확인합니다.
- **Codex:** 원래 host 방식과 플래그를 유지합니다. `-c`로 연 TUI는 내장 app-server, `-c` 없는 resume은 공유 daemon을 사용합니다. 원래 플래그 그대로 종료 후 다시 열고, exec 대화는 exec 방식으로 resume합니다. 공유 daemon 기반 TUI를 다시 여는 것만으로 MCP가 새로 실행된다고 보장하지 않습니다.
- **Codex daemon reload:** `config/mcpServer/reload`는 격리 app-server에서 확인한 실험적 방법입니다. 공유 daemon에서는 다른 프로젝트를 포함한 모든 thread에 영향을 줄 수 있으므로 사용자가 영향 범위를 판단할 때만 선택합니다. x-broker와 PM은 이를 자동 실행하지 않습니다.
- **Windows:** 0.17.3 이상 npm launcher는 검증된 전용 실행파일 사본을 사용하므로 세션을 유지한 채 `npm install -g`로 갱신할 수 있습니다. 이전 launcher에서 처음 갱신할 때는 실행 중인 asb-client를 종료해야 합니다. 캐시를 쓸 수 없어 원본 실행으로 fallback했다는 stderr 안내가 있으면 그 세션도 업그레이드 전에 종료하세요. 실행 중 client 버전은 MCP 재연결 때 바뀝니다.
- **Kimi:** 업그레이드·재연결은 미측정입니다. 설치 또는 설정 버전을 갱신하고 Kimi를 재시작하세요.

daemon `restart`·`update`는 같은 daemon의 모든 대화 작업을 끊을 수 있습니다. daemon steer는 재시작 뒤 기록·대기열로 확인하며 미확인 메시지와 뒤의 전달을 보류합니다. embedded·Windows 전환과 기존 hook·queue의 짧은 저장 창에는 중복 가능성이 남습니다. 프로젝트에 맞춰 daemon(즉시 전달·재시작 중복 보호)과 embedded(대화별 환경·도구 경계 전달)를 선택하고, 한 대화에서는 모드를 유지하세요.

Codex는 도구 목록을 세션마다 고정하므로 새 client가 추가한 도구는 Codex 세션을 다시 열어야 보입니다. Claude는 `/mcp` Reconnect로 도구 목록을 다시 읽습니다.

재연결 뒤 `auth_status.clientVersion`, 같은 등록 ID·이름, `get_session.automaticDeliveryReady`와 실제 메시지 수신 재개를 확인합니다. 업그레이드하려고 등록을 retire하거나 새로 attach하지 않습니다.
<!-- /xbroker-docs:upgrade -->

## 버전 호환

| 조합 | 사용할 수 있는 기능 |
| --- | --- |
| 서버 0.17.3 + 클라이언트 0.17.2 | 기존 기능은 유지되지만 새 도구는 client 내장 목록에 없어 사용할 수 없습니다. ACK 미협상은 기존 전달 방식입니다. |
| 클라이언트 0.17.3 + 서버 0.17.2 | 새 서버 도구는 미지원 안내, ACK는 미협상입니다. 기존 기능과 로컬 xbroker_docs는 사용할 수 있습니다. |
| 서버 0.17.2 + 클라이언트 0.17.1 | 기존 연결·메시지와 서버의 프로젝트 기록 격리·관리 화면을 지원합니다. 새 도구 입력과 프로젝트 종료 안내·수신 프로세스 보호에는 클라이언트도 0.17.2가 필요합니다. |
| 클라이언트 0.17.2 + 서버 0.17.1 | 기존 연결·메시지를 지원합니다. 프로젝트 종료 판단·수신 프로세스 보호는 지원하지 않습니다. `expectRegistrationId`는 `unsupported`, Kimi 연결은 `unsupported-server`로 거부합니다. |

업데이트 순서는 **전체 인스턴스 데이터 백업 → 서버 0.18.1 → npm 클라이언트 0.18.1(0.18.0 사용자는 선택 사항) → 각 대화 재연결**입니다.

1. 서버를 중지하고 전체 인스턴스 데이터와 기존 클라이언트 상태를 백업합니다. 서버 메모리 대기열은 재시작 때 사라지므로 가능한 한 대기 메시지를 먼저 비웁니다.
2. 같은 데이터 경로로 서버 0.18.1을 시작합니다. HTTP 허용 OFF인 평문 연결은 localhost도 거부하므로 TLS proxy 신뢰 설정이나 명시적 HTTP 허용 정책을 먼저 준비하세요. 기존 저장 형식의 필수 이전은 없으며, 이전 버전에서 올리는 경우에는 [업그레이드 안내](https://github.com/xelexis-dev/agent-session-broker-deploy/blob/main/UPGRADE_PATH.md)를 먼저 따르세요.
3. 전역 설치는 `npm install -g @xelexis/x-broker@0.18.1`으로 갱신합니다. npx 사용자는 MCP 설정의 고정 버전을 바꾸고 `npx -y @xelexis/x-broker@0.18.1 --version`으로 준비합니다. Windows에서 구 launcher를 처음 교체할 때는 실행 중인 asb-client를 한 번 모두 종료하세요. 새 launcher라도 cache fallback 안내가 있으면 해당 연결을 종료한 뒤 설치합니다.
4. Claude는 `/mcp`에서 재연결합니다. Codex는 원래 실행 방식과 플래그로 세션을 다시 열어 도구 목록과 새 clientVersion을 확인합니다. 공유 daemon 재개만으로 MCP 교체를 단정하지 마세요. Kimi 업그레이드는 미측정입니다. 같은 등록 ID·이름·수신 준비와 peer 메시지 실제 수신을 확인하며 새 attach/retire로 등록을 바꾸지 않습니다.

새 서버 도구와 메시지 ACK에는 서버와 클라이언트 모두 0.17.3이 필요합니다. 클라이언트는 내장 도구 목록을 사용하므로 구 client 재연결만으로 새 도구가 생기지 않습니다. ACK는 host 인계까지이며 모델 읽음 확인이 아닙니다. 구 client로 내릴 때 발급된 미확인 메시지가 있으면 고정 최대 10분 동안 재시도 가능한 `storage`로 보호하고 이후 legacy 전달을 허용합니다.

롤백은 서버를 중지하고 **업그레이드 전 전체 데이터 백업과 이전 실행파일을 함께 복원**합니다. `control.db`만 되돌리지 마세요. 백업 이후 변경은 복원되지 않습니다. ACK 대기열은 메모리 전용이며 재시작·롤백으로 사라집니다. 0.17.2는 해결·무시 리포트를 닫힘으로 읽지만 구서버 쓰기는 확장 상태·메모·기록을 잃고 32KiB 초과 record의 상태 변경이 거부될 수 있습니다.

daemon `restart`·`update`는 같은 daemon의 모든 대화 작업을 끊을 수 있습니다. daemon steer는 재시작 뒤 기록·대기열로 확인하며 미확인 메시지와 뒤의 전달을 보류합니다. embedded·Windows 전환과 기존 hook·queue의 짧은 저장 창에는 중복 가능성이 남습니다. 프로젝트에 맞춰 daemon(즉시 전달·재시작 중복 보호)과 embedded(대화별 환경·도구 경계 전달)를 선택하고, 한 대화에서는 모드를 유지하세요.

서버 버전별로 지원하는 클라이언트 최소 버전을 관리합니다. `client-incompatible` 또는 `server-incompatible` 안내가 나오면 표시된 최소 버전을 확인하세요. 클라이언트는 MCP 설정의 npm 버전을 지원 버전으로 바꾼 뒤 Claude에서는 `/mcp`로 재연결하고 Codex에서는 앱을 다시 시작합니다. 서버가 너무 오래된 경우에는 서버도 지원 버전으로 업데이트해야 합니다. `auth_status`에서 클라이언트·서버 버전과 호환 여부를 확인할 수 있습니다.

0.16 이하 클라이언트는 상세 안내 대신 다음 일반 오류만 표시할 수 있습니다:

> Current session identity or automatic registration is unavailable; verify this MCP client's parent connection.

호환 정책 변경 후 이 오류가 나타나면 `auth_status`로 클라이언트 버전을 확인하고, MCP 설정의 npm 버전을 업데이트한 뒤 Claude는 `/mcp`, Codex는 앱 재시작으로 다시 연결하세요.
