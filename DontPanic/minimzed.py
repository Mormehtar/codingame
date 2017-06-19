_,_,_,z,x,_,_,e=input().split();d={z:int(x)}
for i in range(int(e)):f,p=input().split();d[f]=int(p)
while 1:v,b,n=input().split();b=int(b);t=d.get(v);print("WAIT"if t is None or t==b or not(t<b and n=='RIGHT'or t>b and n=='LEFT')else"BLOCK")