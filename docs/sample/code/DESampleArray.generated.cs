using System.Collections.Generic;

public class DESampleArray_StructColArr
{
    public string name;
    public int value;
}

public class DESampleArray_StructRowArr
{
    public string name;
    public int value;
}

/// <summary>
/// 배열 샘플 테이블 항목
/// </summary>
public class DESampleArray
{
    public int id;

    /// <summary>
    /// 열방향 배열
    /// </summary>
    public List<int> colArr;

    /// <summary>
    /// 행방향 배열
    /// </summary>
    public List<int> rowArr;

    /// <summary>
    /// 구조체 열방향 배열
    /// </summary>
    public List<DESampleArray_StructColArr> structColArr;

    /// <summary>
    /// 구조체 행방향 배열
    /// </summary>
    public List<DESampleArray_StructRowArr> structRowArr;
}
