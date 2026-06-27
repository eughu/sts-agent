# STS Agent

一个给《杀戮尖塔 1》（Slay the Spire 1）准备的本地多子 agent 辅助器。它不会读取游戏内存、不会自动操作游戏，也不会替你作弊；你把当前局面和候选选项输入到命令行，它会用多个子 agent 给出可解释的建议，帮助你做通关决策。

说人话：它不是“保证通关”的自动驾驶。杀戮尖塔有随机地图、随机奖励、敌人行动、抽牌顺序和大量边界局面，单靠一个短脚本不可能稳定替你赢。但这个项目的目标是做一个认真可扩展的爬塔参谋：它会诊断卡组缺口，结合 boss/精英威胁，给路径、卡牌、商店、遗物和战斗线排序。

## 子 agent 设计

- `route-agent`：路径选择。根据血量、金币、楼层、精英、火堆、商店、问号和普通战斗来评分。
- `combat-agent`：战斗/技能出牌。根据斩杀、来伤、格挡、输出、成长、抽牌、药水使用来评分。
- `card-choice-agent`：卡牌奖励选择。根据角色、当前幕数、卡组大小、前期输出、后期成长、格挡和抽牌需求来评分。
- `relic-agent`：遗物选择。根据能量、抽牌、防御、角色机制和常见 boss 遗物风险来评分。
- `shop-agent`：商店选择。根据金币、删牌、遗物、卡牌、药水、花费比例来评分。
- `run-profile`：共享诊断器。分析当前卡组是否缺前期输出、AOE、格挡、抽牌、成长，以及低血量/高升阶风险。
- `SpireCoordinator`：总控 agent。按主题调用对应子 agent，并输出排名、理由和风险提示。

## 关键信息输入

越多上下文，建议越准。常用输入包括：

- `--character`：角色，支持 `ironclad`、`silent`、`defect`、`watcher`
- `--act`：当前幕，支持 `act1` 到 `act4`
- `--floor`：楼层
- `--hp` / `--max-hp`：当前血量和最大血量
- `--gold`：金币
- `--deck`：当前卡组，逗号分隔
- `--relics` / `--potions`：遗物和药水，逗号分隔
- `--boss`：已知 boss，例如 `Slime Boss`、`Hexaghost`、`Guardian`
- `--next-elite`：已知或推测的精英，例如 `Gremlin Nob`、`Sentries`、`Slavers`
- `--ascension`：升阶等级

## Windows 安装

1. 安装 Python 3.10 或更新版本：
   - 推荐从 <https://www.python.org/downloads/windows/> 安装。
   - 安装时勾选 `Add python.exe to PATH`。

2. 克隆仓库：

   ```powershell
   git clone <你的 GitHub 仓库地址>
   cd sts-agent
   ```

3. 创建虚拟环境并安装：

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   py -m pip install --upgrade pip
   py -m pip install -e .
   ```

4. 验证命令可用：

   ```powershell
   sts-agent --help
   ```

如果 PowerShell 禁止激活脚本，可以临时允许当前用户脚本：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 使用示例

### 卡牌奖励

```powershell
sts-agent card `
  --character ironclad `
  --act act1 `
  --floor 5 `
  --hp 60 `
  --max-hp 80 `
  --gold 120 `
  --boss "Slime Boss" `
  --ascension 10 `
  --deck "Strike,Strike,Defend,Shrug It Off" `
  --option "Demon Form" `
  --option "Cleave" `
  --option "Skip"
```

### 路径选择

选项格式是：

```text
名称|标签1,标签2|元数据key=value,key=value
```

```powershell
sts-agent route `
  --character silent `
  --act act1 `
  --floor 8 `
  --hp 35 `
  --max-hp 70 `
  --gold 180 `
  --boss "Hexaghost" `
  --next-elite "Gremlin Nob" `
  --deck "Strike,Defend,Neutralize,Survivor,Blade Dance" `
  --option "Elite into campfire|elite,campfire" `
  --option "Two hallways then shop|hallway,shop" `
  --option "Safe question path|question,campfire"
```

### 战斗出牌

```powershell
sts-agent combat `
  --character defect `
  --act act2 `
  --floor 24 `
  --hp 42 `
  --max-hp 72 `
  --deck "Zap,Dualcast,Defragment,Glacier,Compile Driver" `
  --option "Play Defragment|scaling|incoming=6,energy=1" `
  --option "Glacier plus Zap|block,orb|incoming=18,energy=3" `
  --option "Use attack potion|potion,attack|incoming=18,lethal=false"
```

### 商店选择

```powershell
sts-agent shop `
  --character watcher `
  --act act2 `
  --floor 22 `
  --hp 50 `
  --max-hp 72 `
  --gold 260 `
  --boss "Collector" `
  --deck "Eruption,Vigilance,Strike,Defend,Tantrum,Rushdown" `
  --option "Card remove|remove|cost=125" `
  --option "Rushdown|draw,stance,scaling|cost=90" `
  --option "Potion|potion|cost=50"
```

## 标签速查

你可以给候选项手动加标签，让 agent 更懂你的意图。

- 路径：`elite`、`campfire`、`shop`、`question`、`hallway`、`boss`
- 战斗：`attack`、`block`、`scaling`、`draw`、`potion`
- 商店：`remove`、`relic`、`potion`、`premium`
- 遗物：`energy`、`draw`、`block`、`defense`、`shiv`、`orb`
- 卡牌：很多常见卡牌会自动识别，也可以手动补标签。

## 开发和测试

```powershell
py -m pip install -e ".[dev]"
py -m pytest
```

## 当前局限

- 这是启发式 agent，不是完美 AI，也不会读取游戏画面或存档。
- 内置卡牌知识库覆盖常见强牌、机制、boss/精英威胁，后续可以继续扩展。
- 建议用于辅助思考，最终仍要结合敌人、药水、boss、卡组具体循环来判断。

## 下一步可以扩展

- 增加交互式 TUI，让你一边玩一边填局面。
- 增加更多卡牌、遗物、敌人和 boss 的专门规则。
- 增加“当前 boss/精英预测”输入。
- 增加保存 run 历史和复盘功能。
