"""Database models used in the prediction app."""
from django.db import models

class PredictionVariable(models.Model):
    """Model containing information on variables used in predictions."""
    VARIABLE_TYPES = (('IN', "Input variable"), ('OUT', "Output variable"))

    name = models.CharField(max_length=100, primary_key=True)
    label = models.CharField(max_length=255, blank=True)

    type = models.CharField(choices=VARIABLE_TYPES, default='IN', max_length=3)

    def __unicode__(self):
        """Returns a unicode description of this object.

        Returns:
            The unicode description of the label if the label is set,
            else the unicode description of the name.
        """
        return unicode(self.label or self.name)

    def __str__(self):
        return unicode(self).encode('ascii', 'xmlcharrefreplace')

    def __repr__(self):
        return "PredictionVariable(%s)" % (self,)


class PredictionVariableValue(models.Model):
    """Model containing the possible values for a variable."""
    variable = models.ForeignKey('PredictionVariable', related_name="values")
    value = models.FloatField()

    def __unicode__(self):
        return unicode(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "PredictionVariableValue(%s)" % (self,)


class Prediction(models.Model):
    """Model containing probabilistic mappings from input to output values."""
    input_variable = models.ForeignKey('PredictionVariable', related_name='+')
    input_value = models.FloatField()
    output_variable = models.ForeignKey('PredictionVariable', related_name='+')
    output_value = models.FloatField()
    probability = models.FloatField()

    def __unicode__(self):
        return u"P(%s=%s|%s=%s) = %s" % (
                self.output_variable.name, self.output_value,
                self.input_variable.name, self.input_value, self.probability)

    def __str__(self):
        return unicode(self).encode('ascii', 'xmlcharrefreplace')

    def __repr__(self):
        return "Prediction(%s)" % (self,)

    @classmethod
    def get_table(cls, input_variable, input_value, output_variable,
            as_dict=False):
        """Returns a mapping from output values to probabilities.

        Parameters:
            input_variable  -   The variable on which to base the prediction on
            input_value     -   The selected value of the input variable
            output_variable -   The variable that is being predicted
            as_dict         -   Whether the resulting mapping should be a dict
                                (default: False)

        Returns:
            A list of tuples (output_value, probability) when as_dict is False,
            else a dictionary (output_value: probability)
        """
        # Retrieve all possible output values
        values = output_variable.values.values_list('value', flat=True)
        # Retrieve known output value probabilities, given an input value
        predictions = cls.objects\
                .filter(output_variable=output_variable,
                        input_variable=input_variable,
                        input_value=input_value
                ).values_list('output_value', 'probability')
        if len(predictions) == 0:
            # If there are no predictions for the given input_value,
            #  try to use the closest input_value that does have predictions.
            predictions = cls.objects\
                    .filter(output_variable=output_variable,
                            input_variable=input_variable
                    ).extra(select={'distance':"ABS( input_value - %s )"},
                            select_params=(input_value,),
                            order_by=['distance']
                            ).values_list('output_value', 'probability')[:1]
        # Construct a prediction table
        table = dict(zip(values, [0.0]*len(values)))
        # Insert the predicted probabilities in the table
        table.update(dict(predictions))
        # Return the prediction table in the desired format
        return table if as_dict else table.items()
