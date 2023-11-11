#include <stdio.h>
#define MAXE 100
#define MAXV 100

typedef struct
{
    int vex1;   // 边的起始顶点
    int vex2;   // 边的终止顶点
    int weight; // 边的权值
} Edge;

void kruskal(Edge E[], int n, int e)
{
    int i, j, m1, m2, sn1, sn2, k, sum = 0;
    int vset[n + 1];
    for (i = 1; i <= n; i++) // 初始化辅助数组
        vset[i] = i;
    k = 1;        // 表示当前构造最小生成树的第k条边，初值为1
    j = 0;        // E中边的下标，初值为0
    while (k < e) // 生成的边数小于e时继续循环
    {
        m1 = E[j].vex1;
        m2 = E[j].vex2; // 取一条边的两个邻接点
        sn1 = vset[m1];
        sn2 = vset[m2];
        // 分别得到两个顶点所属的集合编号
        if (sn1 != sn2) // 两顶点分属于不同的集合，该边是最小生成树的一条边
        {               // 防止出现闭合回路
            printf("v%d-v%d=%d\n", m1, m2, E[j].weight);
            sum += E[j].weight;
            k++;        // 生成边数增加
            if (k >= n) // 没有边或者找到的边>顶点数减1都退出循环
                break;
            for (i = 1; i <= n; i++) // 两个集合统一编号
                if (vset[i] == sn2)  // 集合编号为sn2的改为sn1
                    vset[i] = sn1;
        }
        j++; // 无论上一条边是否被收入最下生成树，都要扫描下一条边
        // k++与j++的位置不同，k++在循环内部(只有满足条件才能被收入最小生成树)，j++在循环外部
    }
    // printf("the lowest weight=%d\n", sum);
    printf("%d\n", sum);
}

void swap(Edge arr[], int low, int high)
{
    Edge temp;
    temp = arr[low];
    arr[low] = arr[high];
    arr[high] = temp;
}

int fun(Edge arr[], int low, int high)
{
    int key;
    Edge lowx;
    lowx = arr[low];
    key = arr[low].weight;
    while (low < high)
    {
        while (low < high && arr[high].weight >= key)
            high--;
        if (low < high)
            swap(arr, low, high);
        // arr[low++]=arr[high];

        while (low < high && arr[low].weight <= key)
            low++;
        if (low < high)
            swap(arr, low, high);
        // arr[high--]=arr[low];
    }
    arr[low] = lowx;
    return low;
}

void quick_sort(Edge arr[], int start, int end)
{
    int pos;
    if (start < end)
    {
        pos = fun(arr, start, end);
        quick_sort(arr, start, pos - 1);
        quick_sort(arr, pos + 1, end);
    }
}

void gen(Edge E[], int vertex, int edge)
{
    for (int i = 0; i < edge; i++)
        scanf("%d%d%d", &E[i].vex1, &E[i].vex2, &E[i].weight);
}

int main()
{
    Edge E[MAXE];
    int vertex, edge;
    // printf("请输入顶点数和边数：");
    scanf("%d%d", &vertex, &edge);
    gen(E, vertex, edge);
    quick_sort(E, 0, edge - 1);
    kruskal(E, vertex, edge);
}
