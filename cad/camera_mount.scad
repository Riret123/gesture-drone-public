// Concept only, millimeters; verify fit and loads. No flight qualification.
width=50; depth=35; thickness=3; hole=3.2; spacing=30;
assert(width>spacing+hole && depth>hole+8 && thickness>0);
difference(){
  cube([width,depth,thickness],center=true);
  for(x=[-spacing/2,spacing/2])
    translate([x,0,0]) cylinder(h=thickness+2,d=hole,center=true,$fn=32);
}
