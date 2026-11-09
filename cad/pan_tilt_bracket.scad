// L bracket concept; mm; no servo-specific fit or load rating.
width=45; depth=30; height=30; wall=4; hole=3.2;
assert(width>2*wall && depth>wall && height>wall && hole>0);
difference(){
  union(){cube([width,depth,wall]); cube([width,wall,height]);}
  for(x=[width/4,3*width/4]){
    translate([x,depth/2,-1]) cylinder(h=wall+2,d=hole,$fn=32);
    translate([x,wall+1,height*0.65]) rotate([90,0,0]) cylinder(h=wall+2,d=hole,$fn=32);
  }
}
