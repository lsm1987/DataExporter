using System.Collections.Generic;

/// <summary>
/// 보상 획득 조건
/// </summary>
public struct DESampleComplex_Rewards_Condition
{
    /// <summary>
    /// 최초 클리어
    /// </summary>
    public bool firstClear;

    /// <summary>
    /// 클리어 시간 제한. 단위: 초
    /// </summary>
    public int timeLimit;
}

/// <summary>
/// 보상 획득 시 메시지
/// </summary>
public struct DESampleComplex_Rewards_Messages
{
    /// <summary>
    /// 메시지
    /// </summary>
    public string text;

    /// <summary>
    /// 메시지 등장 딜레이. 단위: 초
    /// </summary>
    public float delay;
}

public struct DESampleComplex_Rewards
{
    /// <summary>
    /// 아이템 ID
    /// </summary>
    public int itemId;

    /// <summary>
    /// 아이템 수량
    /// </summary>
    public int count;

    /// <summary>
    /// 보상 획득 조건
    /// </summary>
    public DESampleComplex_Rewards_Condition condition;

    /// <summary>
    /// 보상 획득 시 메시지 목록
    /// </summary>
    public List<DESampleComplex_Rewards_Messages> messages;
}

public struct DESampleComplex_Exp
{
    /// <summary>
    /// 계정 경험치
    /// </summary>
    public int accountExp;

    /// <summary>
    /// 캐릭터 경험치
    /// </summary>
    public int characterExp;
}

/// <summary>
/// 복합 샘플 테이블 항목
/// </summary>
public class DESampleComplex
{
    /// <summary>
    /// ID
    /// </summary>
    public string id;

    /// <summary>
    /// 스테이지명
    /// </summary>
    public string name;

    /// <summary>
    /// 개방 시간
    /// </summary>
    public List<DEContentsOpenTime> openTimes;

    /// <summary>
    /// 보상 아이템 목록
    /// </summary>
    public List<DESampleComplex_Rewards> rewards;

    public DESampleComplex_Exp exp;
}
