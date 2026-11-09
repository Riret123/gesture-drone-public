// Rover pad frame concept, mm; separate deck required. Not load qualified.
side=240; rim=15; height=8; hole=4.2;
assert(side>4*rim && height>0 && hole>0 && hole<rim);
difference(){
  cube([side,side,height],center=true);
  cube([side-2*rim,side-2*rim,height+2],center=true);
  for(x=[-side/2+rim/2,side/2-rim/2])
    for(y=[-side/2+rim/2,side/2-rim/2])
      translate([x,y,0]) cylinder(h=height+2,d=hole,center=true,$fn=32);
}
