using System.Collections.Generic;

/// <summary>
/// 컨텐츠 개방 시간
/// </summary>
public struct DEContentsOpenTime
{
    /// <summary>
    /// 입장 요일
    /// </summary>
    public DEDayOfWeek dayOfWeek;

    /// <summary>
    /// 입장 시작 시간
    /// </summary>
    public string startTime;

    /// <summary>
    /// 입장 종료 시간
    /// </summary>
    public string endTime;
}
