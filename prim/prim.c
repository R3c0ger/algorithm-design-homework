#include <stdio.h>
#define VexMax 25
#define Inf 0x7fffffff // 32位的最大值 在本程序中代表∞

typedef struct
{
	int Vex[VexMax];
	int Arc[VexMax][VexMax];
	int arcnum, vexnum;
} MGraph;

void Create_G(MGraph *G) // 建立该图
{
	// printf("请输入路由拓扑的顶点数，边数：\n");
	scanf("%d%d", &G->vexnum, &G->arcnum);
	// printf("请依次输入顶点序号：\n");
	for (int i = 1; i <= G->vexnum; i++) // 初始化顶点数组
	{
		// int m;
		// printf("第%d个顶点为：", i);
		// scanf("%d", &m);
		// G->Vex[i] = m;
		G->Vex[i] = i;
	}
	for (int i = 1; i <= G->vexnum; i++) // 初始化邻接矩阵，先令所有边的权重为∞
		for (int j = 1; j <= G->vexnum; j++)
			G->Arc[i][j] = G->Arc[j][i] = Inf; // 有些代码实现的时候，会令i=j的对角元素置0，因为本人又菜又懒，直接Inf了

	for (int i = 1; i <= G->arcnum; i++) // 按照用户需求。建立边，对边赋值
	{
		int weight;
		int v1, v2;
		// printf("请输入第%d条的边的邻接点(vi, vj)和对应边的权值：", i);
		scanf("%d%d%d", &v1, &v2, &weight);
		G->Arc[v1][v2] = G->Arc[v2][v1] = weight; // 对建立边的邻接矩阵赋值
		//这是建立无向图，所以可以G->Arc[v1][v2] = G->Arc[v2][v1]，建立有向图的时候要注意不要这样写
	}
}

int Prim(int Arc[VexMax][VexMax], int n) // Prim算法
{
	int lowcost[VexMax]; // 在Prim算法中，要建立两个数组 lowcost[],mst[]，记住在循环时要重置更新
	int mst[VexMax];
	int min = Inf; // 这些变量要记得初始化，根据要实现的不同功能，初始化不同的值
	int minid = 0; // 用来标记可以并入MST中的顶点标号
	int sum = 0;   // 用来表示最短路径长度，每次更新完都加上lowcost[i]
	// 假设从输入的第一个顶点开始构建最小生成树，在该算法中需要两个数组,mst[k],lowcost[k]

	// 初始化
	mst[1] = 0;					 // 表明第一个节点已经在目前正在构建的MST树中
	for (int i = 1; i <= n; i++) // 在构建MST时，首先要初始化两个数组
	//第1个for循环进行初始化，初始化lowcost数组，mst[i]=1
	{
		lowcost[i] = Arc[1][i]; // 因为是从第一个顶点开始的直接去遍历之前建立好的邻接矩阵中 第一行，找到与第一个节点相连的边，并把权赋给lowcost[i]
		mst[i] = 1;				// 在初始化的时候，将除第一个节点之外的各节点都设置为mst[i]=1
	}
	// mst[1] = 0;//表明第一个节点已经在目前正在构建的MST树中  此行顺序无所谓，也可写在上面mst[1]=0显示的位置，只要记住初始化即可

	for (int m = 2; m <= n; m++) // 遍历其他n-1个点
	//第2个for循环 用来构建MST，又包括两个for循环
	{
		min = Inf; // 这个地方要注意，我第一遍写的时候就忘记重置了，得到的结果是一样的
		minid = 0; // 同理，minid也要重置
		for (int i = 1; i <= n; i++)
		{
			if (lowcost[i] < min && lowcost[i] != 0)
			{
				min = lowcost[i];
				minid = i; // 说明此时minid这个点并入MST中
			}
		}
		lowcost[minid] = 0; //!!!!!!!!!要记住 为了防止后续再次被比较，要令该节点的lowcost[minid]=0
		sum = sum + min;
		printf("v%d-v%d=%d\n", mst[minid], minid, min); // 找到一个顶点输出一次
		for (int j = 2; j <= n; j++)					// 第 3个for循环，是为了更新其他顶点的信息
		// 因为此时又并入了一个顶点，所以还要更新其他顶点的lowcost，取最短的
		{
			if (Arc[minid][j] < lowcost[j])
			{
				lowcost[j] = Arc[minid][j];
				mst[j] = minid;
			}
		}
	}
	return sum; // 返回构建完成的最小生成树的最短路径长度
}

int main()
{
	int summ;
	MGraph G;
	Create_G(&G);
	summ = Prim(G.Arc, G.vexnum);
	// printf("最短路径长度为：%d\n", summ);
	printf("%d\n", summ);
	return 0;
}