package capsis.lib.quest.ringviewer.model;

import javax.swing.JLabel;
import javax.swing.JPanel;

import jeeb.lib.util.ColorGradient;
import jeeb.lib.util.ColorGradientLegend;
import jeeb.lib.util.ColumnPanel;
import jeeb.lib.util.LinePanel;
import jeeb.lib.util.Translator;
import capsis.lib.quest.ringviewer.QuestRing;

/**
 * A model for Modulus Of Rupture for Black Spruce
 * 
 * @author Alexis Achim, F. de Coligny - December 2014
 */
public class QuestBlackSpruceMOR extends QuestModel {
	
	/**
	 * Constructor
	 */
	public QuestBlackSpruceMOR() {
		
		// Set min and max values
		setMinAndMax (73.976, 105); // needed for each model (should be made better)
		
		// Init color gradient
		colorGradient = new ColorGradient((float) minValue, (float) maxValue);
		colorGradient.setGradientColor(BLUE_RED_GRADIENT);

	}
	
	/**
	 * Returns the name of this model
	 */
	public String getName() {
		return Translator.swap("QuestBlackSpruceMOR.name");
	}

	/**
	 * Returns the textual comment to be added under the graph (may contain
	 * litterature references
	 */
	public String getCaption() {
		return Translator.swap("QuestBlackSpruceMOR.caption");
	}

	/**
	 * Returns the value of this model for the given ring
	 */
	public double getValue(QuestRing ring) {
		
		double b1 = 33.016;
		double b2 = 0.065;
		double b3 = 73.976;
		double b4 = -8.796;
		
		double v = (b1 + b4 * ring.width_mm) * (1 - Math.exp(-b2 * ring.cambialAge)) + b3;

//		// update min and max values to have a correct legend (see below)
//		minValue = Math.min(minValue, v);
//		maxValue = Math.max(maxValue, v);
		
		return v;

	}

	/**
	 * Returns a graphical legend to be added next to the graph. This function
	 * should be called after the calls to getValue () to have correct values for
	 * minValue and maxValue.
	 */
	public JPanel getLegend() {
		ColumnPanel c1 = new ColumnPanel();

		LinePanel l2 = new LinePanel();
		l2.add(new JLabel(getName ()));
		l2.addStrut0();
		c1.add(l2);

		ColorGradientLegend gradientLegend = new ColorGradientLegend(colorGradient);
		LinePanel l1 = new LinePanel();
		l1.add(gradientLegend);
		l1.addStrut0();
		c1.add(l1);

		c1.addStrut0();

		return c1;
	}

}
