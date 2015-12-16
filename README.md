# An Elastic Distributed SDN Controller 

2015 Fall CSE222A  Group 8 Project


Implement a load balancing algorithm between OpenFlow controllers and switches

- Use [Mininet](https://github.com/mininet/mininet) and [Ryu Python](http://osrg.github.io/ryu/).
- Safely migrate switches between controllers


## Results

### Response Time Before Migration

![](https://raw.githubusercontent.com/BenBBear/Elastic-Controller/data-analysis/Figures/new/restime-4-4.png)


The respond time of Controller B has a higher respond time than the Controller A. Because B is under more traffic pressure.

### Response Time After Migration

![](https://github.com/BenBBear/Elastic-Controller/blob/data-analysis/Figures/new/restime-5-3.png)

We can see the the response time of Controller B reduces a lot while that of Controller A goes up because of the balanced traffic. While the weird thing is the response time of Controller A is increased too much, with two big hazards. We think the network congestion could be the possible cause.

### Throughput Before Migration 

![](https://raw.githubusercontent.com/BenBBear/Elastic-Controller/data-analysis/Figures/new/throughput-4-4.png)

It's clear to see that the Controller B is heavily loaded, while the A still has a lot of unused bandwidth. However, the overall performance of the controller network already reaches the ceiling after the sending rate of 1500 packets/s because of congestion.

### Throughput After Migration

![](https://raw.githubusercontent.com/BenBBear/Elastic-Controller/data-analysis/Figures/new/througput-5-3.png)

After the migration, we see significant improvement.

- The sum of these two lines is significantly higher after migration, which means the overall throughput is improved.
- The threshold of sending rate is around 2500 packets/s, compared to the 1500 packets/s before.

## Conclusions

The result has showed that after migration, the load is more balanced between two controllers, especially for throughput. The overall throughput increased after migration. However, the result of the response time is little weird. We think the main reason for this is the network congestion. Since Mininet only provides a very limited bandwidth network, when we increase the packet sending rate, a lot of packets will be dropped and resent because of congestion, therefore disrupt our test result.


We conduct our experiment on a very simple network topology, with only one application: packet sending application. It is a proof of concept experiment. For future work, we need to deploy the system on large scale network, with real world network application running on top of it, to see how it performs and how much it can help to balance the load within the network.
