%% first graph

hold on
cn = [1,2,3,4,5];
tp = [12,20,27,34,40];
mkgraph(cn,tp,'-r.');  
ylabel('Throughput (in x10^3 flows/seconds)');
xlabel('Number of controller nodes');
axis([0,6,0,100])
title('Controller throughput');
hold off

figure

hold on
a3x = [19,20,21,22,22.5,24];
a3y = [0,0.5,0.8,0.9,0.94,1];
b1x = [7,8,11,12.5,14.5,16];
b1y = [0,0.5,0.74,0.8,0.9,1];
a2x = [12,13,14,15,16,17];
a2y = [0,0.4,0.6,0.8,0.9,1];
b2x = [12.3,13.1,14.4,15,16.9,17];
b2y = [0,0.5,0.62,0.78,0.88,1];
mkgraph(a3x,a3y,'-r.');
mkgraph(b1x,b1y,'-g.');
mkgraph(a2x,a2y,'-b.');
mkgraph(b2x,b2y,'-c.');
axis([0,25,0,1]);
ylabel('Probability');
xlabel('Response time (in msec)');
title('Impact of switch migration');
legend('A with 3 switch','B with 1 switch','A with 2 switch','B with 2 switch');
hold off;  
    