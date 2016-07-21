/*
 * Capsis 4 - Computer-Aided Projections of Strategies in Silviculture
 *
 * Copyright (C) 2000-2001  Francois de Coligny
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package capsis.extension.workingprocess;

import java.util.ArrayList;
import java.util.Collection;

import jeeb.lib.util.Log;
import jeeb.lib.util.Translator;
import capsis.extension.PaleoWorkingProcess;
import capsis.kernel.extensiontype.GenericExtensionStarter;
import capsis.lib.economics.BillBookCompatible;
import capsis.lib.economics.BillBookSpecies;
import capsis.lib.economics.Producer;
import capsis.lib.economics.Product;


/**	Forwarding
*
*	@author O. Pain - october 2007
*/
public class Forwarding extends PaleoWorkingProcess {

	static {
		Translator.addBundle("capsis.extension.workingprocess.Forwarding");
	}


	/**	Phantom constructor.
	*	Only to ask for extension properties (authorName, version...).
	*/
	public Forwarding () {}

	/**	Official constructor. Uses an ExtensionStarter.
	*/
	public Forwarding (GenericExtensionStarter s) throws Exception {
		super (s);
	}

	/**	Extension dynamic compatibility mechanism.
	*	This matchwith method checks if the extension can deal (i.e. is compatible) with the referent.
	*/
	public boolean matchWith (Object referent) {	// referent is a not translated product name
		if (!(referent instanceof String)) {return false;}
		String productName = (String) referent;
		return getInputProductNames ().contains (productName);
	}

	/**	Extension interface */
	public String getName () {
		return Translator.swap ("Forwarding");
	}

	/**	Extension interface */
	public String getVersion () {return VERSION;}
	public static final String VERSION = "1.0";

	/**	Extension interface */
	public String getAuthor () {return "O. Pain";}

	/**	Extension interface */
	public String getDescription () {return Translator.swap ("Forwarding.description");}

	public ForwardingStarter getStarter () {return (ForwardingStarter) starter;}

	/**	WorkingProcess superclass
	*	List of names of input products that this Working Process can possibly process
	*/
	public Collection<String> getInputProductNames () {
		Collection<String> r = new ArrayList<String> ();
		r.add (Product.TREE);
		r.add (Product.LOG);
		r.add (Product.CROWN);
		r.add (Product.BUNDLE);
		return r;
	}

	/**	Producer interface.
	*	List of names of output products that this Working Process can possibly create.
	*/
	public Collection<String> getOutputProductNames () {
		Collection<String> r = new ArrayList<String> ();
		r.add (Product.TREE_ROADSIDE);
		r.add (Product.LOG_ROADSIDE);
		r.add (Product.CROWN_ROADSIDE);
		r.add (Product.BUNDLE_ROADSIDE);
		return r;
	}

	/**	Process input product (starter.input) and create requested output products.
	*	Finally memorize the output ptoducts with addProduct () (see superclass)
	*/
	public void execute () throws Exception {
		super.execute ();	// needed for checks

		// from product and product.getStand (), create some output products and use
		// addProduct () to memorize them in this

		// create Product.TREE_ROADSIDE
		if (starter.requestedOutputProductNames.contains (Product.TREE_ROADSIDE)) {
			Producer producer = this;
			Product input = starter.inputProduct;

			BillBookSpecies species = ((BillBookCompatible) input.getStand ()).getSpecies ();
			String preferredUnit = Product.GREEN_TON;
			double priceInPreferredUnit = species.convert (starter.price, starter.priceUnit, preferredUnit);

			Product output = new Product (Product.TREE_ROADSIDE,
					input.getStand (),
					input.getQty_ts (), // matter conservation with this working process
					input.getQty_tb (),
					input.getQty_m3 (),
					input.getSize (),
					preferredUnit,
					priceInPreferredUnit,
					-1,  // totalFuelConsumption calculation is deferred, see below
					producer);

			double unitFuelConsumption = species.convert (starter.fuel, starter.fuelUnit, preferredUnit);
			double productFuelConsumption = unitFuelConsumption * output.getQuantityInPreferredUnit ();
			output.setTotalFuelConsumption (productFuelConsumption);

			addProduct (output);
			Log.println (Log.INFO, "Forwarding.execute ()", "Forwarding WP made: "+output);
		}

		// create Product.LOG_ROADSIDE
		if (starter.requestedOutputProductNames.contains (Product.LOG_ROADSIDE)) {
			Producer producer = this;
			Product input = starter.inputProduct;

			BillBookSpecies species = ((BillBookCompatible) input.getStand ()).getSpecies ();
			String preferredUnit = Product.GREEN_TON;
			double priceInPreferredUnit = species.convert (starter.price, starter.priceUnit, preferredUnit);

			Product output = new Product (Product.LOG_ROADSIDE,
					input.getStand (),
					input.getQty_ts (), // matter conservation with this working process
					input.getQty_tb (),
					input.getQty_m3 (),
					input.getSize (),
					preferredUnit,
					priceInPreferredUnit,
					-1,  // totalFuelConsumption calculation is deferred, see below
					producer);

			double unitFuelConsumption = species.convert (starter.fuel, starter.fuelUnit, preferredUnit);
			double productFuelConsumption = unitFuelConsumption * output.getQuantityInPreferredUnit ();
			output.setTotalFuelConsumption (productFuelConsumption);

			addProduct (output);
			Log.println (Log.INFO, "Forwarding.execute ()", "Forwarding WP made: "+output);
		}

		// create Product.CROWN_ROADSIDE
		if (starter.requestedOutputProductNames.contains (Product.CROWN_ROADSIDE)) {
			Producer producer = this;
			Product input = starter.inputProduct;

			BillBookSpecies species = ((BillBookCompatible) input.getStand ()).getSpecies ();
			String preferredUnit = Product.GREEN_TON;
			double priceInPreferredUnit = species.convert (starter.price, starter.priceUnit, preferredUnit);

			Product output = new Product (Product.CROWN_ROADSIDE,
					input.getStand (),
					input.getQty_ts (), // matter conservation with this working process
					input.getQty_tb (),
					input.getQty_m3 (),
					input.getSize (),
					preferredUnit,
					priceInPreferredUnit,
					-1,  // totalFuelConsumption calculation is deferred, see below
					producer);

			double unitFuelConsumption = species.convert (starter.fuel, starter.fuelUnit, preferredUnit);
			double productFuelConsumption = unitFuelConsumption * output.getQuantityInPreferredUnit ();
			output.setTotalFuelConsumption (productFuelConsumption);

			addProduct (output);
			Log.println (Log.INFO, "Forwarding.execute ()", "Forwarding WP made: "+output);
		}

		// create Product.BUNDLE_ROADSIDE
		if (starter.requestedOutputProductNames.contains (Product.BUNDLE_ROADSIDE)) {
			Producer producer = this;
			Product input = starter.inputProduct;

			BillBookSpecies species = ((BillBookCompatible) input.getStand ()).getSpecies ();
			String preferredUnit = Product.GREEN_TON;
			double priceInPreferredUnit = species.convert (starter.price, starter.priceUnit, preferredUnit);

			Product output = new Product (Product.BUNDLE_ROADSIDE,
					input.getStand (),
					input.getQty_ts (), // matter conservation with this working process
					input.getQty_tb (),
					input.getQty_m3 (),
					input.getSize (),
					preferredUnit,
					priceInPreferredUnit,
					-1,  // totalFuelConsumption calculation is deferred, see below
					producer);

			double unitFuelConsumption = species.convert (starter.fuel, starter.fuelUnit, preferredUnit);
			double productFuelConsumption = unitFuelConsumption * output.getQuantityInPreferredUnit ();
			output.setTotalFuelConsumption (productFuelConsumption);

			addProduct (output);
			Log.println (Log.INFO, "Forwarding.execute ()", "Forwarding WP made: "+output);
		}

	}

}
