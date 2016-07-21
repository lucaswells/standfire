package fireparadox.model.plant.fmgeom;

import java.io.Serializable;
import java.text.NumberFormat;
import java.util.TreeSet;

import capsis.lib.fire.fuelitem.FiPlant;

import jeeb.lib.util.TicketDispenser;

/**
 * FmGeom is a specific crownGeometry for tree rendering, in the fuel manager. This pattern is
 * composed of a collection of crown diameters, entailing visualization of fire damage
 * 
 * @author S. Griffon - May 2007
 */
public class FmGeom implements Comparable, Cloneable, Serializable {
	
	private int id; //A single identifiant
	private String alias; //An alias to identify the patten
	private String info; // A string that represents the shape of the geom : hDmax -
							// diametersInferior[0] - diametersInferior[1] - ... -
							// diametersSuperior[0] - diametersSuperior[1] - ...
	private TreeSet<FmGeomDiameter> diametersInferior;   //The array of diameters witch are below hDmax, in % of the distance between hBottom (the height of crown bottom) and hDmax
	private TreeSet<FmGeomDiameter> diametersSuperior;   //The array of diameters witch are above hDmax, in % of the distance between hDmax and hTop (the height of crown top)
	private double hDMax; //the height of the maximum crown diameter
	
	public static TicketDispenser idFactory = new TicketDispenser (); //usefull to generate a single identifiant for the object of this class
	
	/** Creates a new instance of FmGeom with default name and default diameter */
	public FmGeom () {
		super ();
		diametersInferior = new TreeSet<FmGeomDiameter> ();
		diametersSuperior = new TreeSet<FmGeomDiameter> ();
		info="";
		alias="";
		id = FmGeom.idFactory.getNext ();
		this.hDMax=50;
	}
	
	public FmGeom (int id) {
		this ();
		this.id = id;
		FmGeom.idFactory.setCurrentValue (id);
	}
	
	// this constructor try to build a FmGeom from plant.crownGeometry and dimensions FP jan 2010
	public FmGeom (FiPlant plant) {
		this ();
		double[][] crownGeom = plant.getCrownGeometry ();
		if (crownGeom == null) {
			this.id = 0;
		} else {
			this.id = FmGeom.idFactory.getNext ();
			double h = plant.getHeight();
			double cbh = plant.getCrownBaseHeight();
			double maxdbhh = plant.getMaxDiameterHeight();
			this.setHDMax(maxdbhh);
			//double maxDiameter = plant.getCrownDiameter();
			for (int ndiam = 0; ndiam < crownGeom.length; ndiam++) {
				if (crownGeom[ndiam][0] * 0.01 * (h - cbh) <= maxdbhh - cbh) {
					double factor = 1d;// (h - cbh) / (maxdbhh - cbh);
					this.addDiametersInferior(new FmGeomDiameter(
							crownGeom[ndiam][0] * factor,
									crownGeom[ndiam][1]));
				// System.out.println("inf:h,d=" + crownProfile[ndiam][0]
					// * factor + "," + crownProfile[ndiam][1]);
				} else {
					double factor = 1d;// (h - cbh) / (h - maxdbhh);
					this.addDiametersSuperior(new FmGeomDiameter(
							crownGeom[ndiam][0] * factor,
									crownGeom[ndiam][1]));
				// System.out.println("sup:h,d=" + crownProfile[ndiam][0]
					// * factor + "," + crownProfile[ndiam][1]);
				}
			}
			FmGeom.idFactory.setCurrentValue (id);
		}
	}
	
	
	@Override
	public FmGeom clone () {
		
		FmGeom fp = null;
		try {
			fp = (FmGeom) super.clone ();
		} catch(CloneNotSupportedException cnse) {
			// Should never be here because we implement Cloneable
		}
		fp.info = new String (info);
		
		fp.diametersInferior = new TreeSet<FmGeomDiameter> ();
		fp.diametersSuperior = new TreeSet<FmGeomDiameter> ();
		
		for (FmGeomDiameter fpd : diametersInferior)	{
			fp.diametersInferior.add (fpd.clone ());
		}
		
		for (FmGeomDiameter fpd : diametersSuperior)	{
			fp.diametersSuperior.add (fpd.clone ());
		}
		
		return fp;
		
	}
	
	public void setHDMax (double hDMax) {
		this.hDMax = hDMax;
	}
	
	public double getHDMax () {
		return hDMax;
	}
	
	public void addDiametersInferior (FmGeomDiameter diameterInferior) {
		this.diametersInferior.add (diameterInferior);
		getInfo ();
	}
	
	public void addDiametersSuperior (FmGeomDiameter diameterSuperior) {
		this.diametersSuperior.add (diameterSuperior);
		getInfo ();
	}
	
	public String getInfo () {
		NumberFormat f = NumberFormat.getIntegerInstance ();
		info=f.format (hDMax);
		for(FmGeomDiameter fdiam : diametersSuperior)  {
			info += " - s"+ f.format(fdiam.getWidth ());
		}
		for(FmGeomDiameter fdiam : diametersInferior) {
			info += " - i"+ f.format(fdiam.getWidth ());
		}
		return info;
	}

	public void setAlias (String alias) {
		this.alias = alias;
	}

	public String getAlias () {
		return alias;
	}

	public String getName () {
		if(alias.length () == 0) {			
			return String.valueOf (id)+" - "+getInfo ();
		} else {
			return alias+"-"+String.valueOf (id)+" - "+getInfo ();
		}
	}
	
	@Override
	public String toString () {
		return getName ();
	}
	
	public void setId (int id) {
		this.id = id;		
	}
	
	public int getId () {
		return id;
	}
	
	public TreeSet<FmGeomDiameter> getDiametersInferior () {
		return diametersInferior;
	}
	
	public TreeSet<FmGeomDiameter> getDiametersSuperior () {
		return diametersSuperior;
	}
	
	
	
	public int compareTo (Object o) {
		FmGeom fPattern = (FmGeom) o;
		return getName ().compareTo (fPattern.getName ());
	}
	
	
}
