s=lambda:input().split()
k=int
*_,z,x,_,_,e=s();d={z:k(x)}
for i in range(k(e)):f,p=s();d[f]=k(p)
while 1:v,b,n=s();b=k(b);t=d.get(v);print("WAIT"if(t is None)or(t==b)or(t>b if n!="LEFT"else t<b)else"BLOCK")