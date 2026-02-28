# Git & GitHub CLI(gh)를 사용한 Push 과정

## 전체 흐름도

```mermaid
flowchart TD
    A["작업 시작"] --> B["git init"]
    B --> C["git remote add origin URL"]
    C --> D["파일 수정 / 생성"]
    D --> E["git add 파일명"]
    E --> F["git commit -m '메시지'"]
    F --> G{"remote 저장소 존재?"}

    G -- "No" --> H["gh repo create --public/--private"]
    H --> I["git push -u origin main"]

    G -- "Yes" --> I

    I --> J{"Push 성공?"}
    J -- "Yes" --> K["완료"]
    J -- "No" --> L{"인증 문제?"}

    L -- "Yes" --> M["gh auth login"]
    M --> I

    L -- "No" --> N{"충돌 발생?"}
    N -- "Yes" --> O["git pull --rebase origin main"]
    O --> P["충돌 해결"]
    P --> F

    N -- "No" --> Q["에러 확인 후 재시도"]
    Q --> I
```

## 단계별 명령어

### 1. 초기 설정

```mermaid
flowchart LR
    A["git init"] --> B["git remote add origin\nhttps://github.com/user/repo.git"]
    B --> C["gh auth login"]
```

| 단계 | 명령어 | 설명 |
|------|--------|------|
| 저장소 초기화 | `git init` | 로컬 Git 저장소 생성 |
| 원격 연결 | `git remote add origin <URL>` | GitHub 원격 저장소 연결 |
| 인증 | `gh auth login` | GitHub CLI 인증 |

### 2. 스테이징 & 커밋

```mermaid
flowchart LR
    A["Working Directory"] -->|"git add"| B["Staging Area"]
    B -->|"git commit"| C["Local Repository"]
```

| 단계 | 명령어 | 설명 |
|------|--------|------|
| 상태 확인 | `git status` | 변경된 파일 확인 |
| 파일 추가 | `git add 파일명` | 스테이징 영역에 추가 |
| 전체 추가 | `git add .` | 모든 변경 파일 추가 |
| 커밋 | `git commit -m "메시지"` | 변경사항 커밋 |

### 3. Push (원격 저장소 전송)

```mermaid
flowchart LR
    A["Local Repository"] -->|"git push"| B["GitHub Remote"]
```

| 단계 | 명령어 | 설명 |
|------|--------|------|
| 최초 Push | `git push -u origin main` | 업스트림 설정 및 Push |
| 이후 Push | `git push` | 변경사항 Push |

### 4. gh CLI로 저장소 생성 (원격 저장소가 없을 때)

```mermaid
flowchart TD
    A["gh repo create repo-name\n--public --source=."] --> B["자동으로 remote 설정됨"]
    B --> C["git push -u origin main"]
```

| 단계 | 명령어 | 설명 |
|------|--------|------|
| 공개 저장소 | `gh repo create 이름 --public --source=.` | 공개 저장소 생성 |
| 비공개 저장소 | `gh repo create 이름 --private --source=.` | 비공개 저장소 생성 |
| 저장소 확인 | `gh repo view` | 저장소 정보 확인 |

### 5. 일반적인 작업 사이클

```mermaid
flowchart TD
    A["코드 수정"] --> B["git status"]
    B --> C["git add ."]
    C --> D["git commit -m '메시지'"]
    D --> E["git push"]
    E --> A
```
